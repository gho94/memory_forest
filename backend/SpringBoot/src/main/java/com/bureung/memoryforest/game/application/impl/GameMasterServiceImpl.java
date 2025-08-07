package com.bureung.memoryforest.game.application.impl;

import com.bureung.memoryforest.ai.AIAnalysisRequest;
import com.bureung.memoryforest.ai.AIAnalysisResponse;
import com.bureung.memoryforest.ai.AIClientService;
import com.bureung.memoryforest.game.application.GameMasterService;
import com.bureung.memoryforest.game.domain.GameDetail;
import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.game.repository.GameDetailRepository;
import com.bureung.memoryforest.game.repository.GameMasterRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Lazy;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

@Service
@RequiredArgsConstructor
@Slf4j
public class GameMasterServiceImpl implements GameMasterService {

    private final GameMasterRepository gameMasterRepository;
    private final GameDetailRepository gameDetailRepository;
    private final AIClientService aiClientService;

    // self-injection for calling transactional methods from async methods
    @Lazy
    @Autowired
    private GameMasterServiceImpl self;

    // 난이도 코드 매핑 메서드들
    private String mapDifficultyCodeToLevel(String difficultyCode) {
        switch (difficultyCode) {
            case "D10001": return "EASY";
            case "D10002": return "NORMAL";
            case "D10003": return "HARD";
            case "D10004": return "EXPERT";
            default: return "NORMAL";
        }
    }

    private String mapDifficultyLevelToCode(String difficultyLevel) {
        switch (difficultyLevel.toUpperCase()) {
            case "EASY": return "D10001";
            case "NORMAL": return "D10002";
            case "HARD": return "D10003";
            case "EXPERT": return "D10004";
            default: return "D10002"; // 기본값: NORMAL
        }
    }

    @Override
    @Transactional(readOnly = true)
    public GameMaster getGameById(String gameId) {
        return gameMasterRepository.findById(gameId)
                .orElseThrow(() -> new RuntimeException("게임을 찾을 수 없습니다: " + gameId));
    }

    @Override
    @Transactional
    public GameMaster saveGame(GameMaster gameMaster) {
        return gameMasterRepository.save(gameMaster);
    }

    @Override
    @Transactional(readOnly = true)
    public List<GameMaster> getAllGames() {
        return gameMasterRepository.findAllByOrderByCreatedAtDesc();
    }

    @Override
    @Transactional(readOnly = true)
    public List<GameMaster> getGamesByDifficultyLevel(String difficultyLevel) {
        String difficultyCode = mapDifficultyLevelToCode(difficultyLevel);
        return gameMasterRepository.findByDifficultyLevelCodeOrderByCreatedAtDesc(difficultyCode);
    }

    @Override
    @Transactional(readOnly = true)
    public List<GameMaster> getGamesByCreationStatusCode(String creationStatusCode) {
        return gameMasterRepository.findByCreationStatusCodeOrderByCreatedAtDesc(creationStatusCode);
    }

    @Override
    @Transactional(readOnly = true)
    public List<GameMaster> getGamesByCreatedBy(String createdBy) {
        return gameMasterRepository.findByCreatedByOrderByCreatedAtDesc(createdBy);
    }

    @Override
    @Transactional
    public String createNewGame(String gameName, String gameDesc, Integer gameCount,
                               String difficultyLevel, String createdBy) {
        String gameId = generateGameId();

        GameMaster gameMaster = GameMaster.builder()
                .gameId(gameId)
                .gameName(gameName)
                .gameDesc(gameDesc)
                .gameCount(gameCount)
                .difficultyLevelCode(mapDifficultyLevelToCode(difficultyLevel))
                .creationStatusCode("CREATING")
                .createdBy(createdBy)
                .build();

        gameMasterRepository.save(gameMaster);
        log.info("새 게임 생성 완료: gameId={}, gameName={}", gameId, gameName);

        return gameId;
    }

    @Override
    @Transactional
    public void updateGameStatus(String gameId, String statusCode, String updatedBy) {
        GameMaster gameMaster = getGameById(gameId);
        gameMaster.setCreationStatusCode(statusCode);
        gameMaster.setUpdatedBy(updatedBy);
        gameMasterRepository.save(gameMaster);

        log.info("게임 상태 업데이트: gameId={}, status={}", gameId, statusCode);
    }

    @Override
    @Transactional(readOnly = true)
    public List<GameMaster> getGamesNeedingAIAnalysis() {
        List<GameDetail> pendingDetails = gameDetailRepository.findPendingAIAnalysis();

        return pendingDetails.stream()
                .map(detail -> getGameById(detail.getGameId()))
                .distinct()
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<GameMaster> getGamesByAIStatus(String aiStatus) {
        List<GameDetail> details = gameDetailRepository.findByAiStatus(aiStatus);

        return details.stream()
                .map(detail -> getGameById(detail.getGameId()))
                .distinct()
                .toList();
    }

    // 비동기 메서드 - 트랜잭션 제거
    @Override
    @Async("aiTaskExecutor")
    public CompletableFuture<Void> processAIAnalysis(String gameId) {
        log.info("=== AI 분석 비동기 처리 시작: gameId={} ===", gameId);
        
        try {
            // 트랜잭션이 필요한 작업은 self를 통해 호출
            self.processAIAnalysisInternal(gameId);
            log.info("=== AI 분석 비동기 처리 완료: gameId={} ===", gameId);
        } catch (Exception e) {
            log.error("=== AI 분석 비동기 처리 실패: gameId={} ===", gameId, e);
            // 실패 시 게임 상태를 FAILED로 변경
            try {
                self.markGameAsFailed(gameId, e.getMessage());
            } catch (Exception ex) {
                log.error("게임 실패 상태 변경 중 오류: gameId={}", gameId, ex);
            }
        }

        return CompletableFuture.completedFuture(null);
    }

    // 트랜잭션이 포함된 내부 처리 메서드
    @Transactional
    public void processAIAnalysisInternal(String gameId) {
        log.info("AI 분석 내부 처리 시작: gameId={}", gameId);
        
        // 1. GameDetail 조회 및 상세 로깅
        List<GameDetail> gameDetails = gameDetailRepository.findByGameIdOrderByGameOrder(gameId);
        log.info("=== 게임 디테일 조회 결과 ===");
        log.info("처리할 게임 디테일 개수: {}", gameDetails.size());
        
        if (gameDetails.isEmpty()) {
            log.warn("⚠️ 게임 디테일이 없습니다: gameId={}", gameId);
            log.info("🔍 데이터베이스에서 직접 조회해보세요:");
            log.info("SELECT * FROM game_detail WHERE game_id = '{}' ORDER BY game_order;", gameId);
            return;
        }
        
        // 2. 각 디테일의 상태 확인
        int needsAnalysisCount = 0;
        for (int i = 0; i < gameDetails.size(); i++) {
            GameDetail detail = gameDetails.get(i);
            boolean needsAnalysis = detail.needsAIAnalysis();
            
            log.info("=== 게임 디테일 #{} 정보 ===", i + 1);
            log.info("gameId: {}, gameSeq: {}, gameOrder: {}", 
                    detail.getGameId(), detail.getGameSeq(), detail.getGameOrder());
            log.info("answerText: '{}'", detail.getAnswerText());
            log.info("aiStatus: '{}'", detail.getAiStatus());
            log.info("needsAIAnalysis(): {}", needsAnalysis);
            log.info("기존 wrongOption1: '{}'", detail.getWrongOption1());
            
            if (needsAnalysis) {
                needsAnalysisCount++;
                log.info("✅ AI 분석 요청 시작: gameId={}, gameSeq={}", 
                        detail.getGameId(), detail.getGameSeq());

                try {
                    // 1. 상태를 ANALYZING으로 변경하고 저장
                    detail.markAIAnalyzing();
                    gameDetailRepository.save(detail);
                    
                    log.info("게임 디테일 상태 ANALYZING으로 변경 완료: gameId={}, gameSeq={}", 
                            detail.getGameId(), detail.getGameSeq());

                    // 2. AI 분석 요청 준비
                    AIAnalysisRequest request = new AIAnalysisRequest();
                    request.setGameId(detail.getGameId());
                    request.setGameSeq(detail.getGameSeq());
                    request.setAnswerText(detail.getAnswerText());
                    
                    // GameMaster에서 난이도 정보 가져와서 설정
                    GameMaster gameMaster = getGameById(gameId);
                    String difficultyLevel = mapDifficultyCodeToLevel(gameMaster.getDifficultyLevelCode());
                    request.setDifficultyLevel(difficultyLevel != null ? difficultyLevel : "NORMAL");

                    log.info("=== AI 서비스 호출 준비 완료 ===");
                    log.info("gameId: {}, gameSeq: {}", request.getGameId(), request.getGameSeq());
                    log.info("answerText: '{}'", request.getAnswerText());
                    log.info("difficultyLevel: {}", request.getDifficultyLevel());
                    log.info("AI 서비스 URL: {}", aiClientService.getAiServiceUrl());

                    // 3. AI 분석 요청 (별도 트랜잭션에서 실행)
                    log.info("🚀 AI 서비스 호출 시작...");
                    AIAnalysisResponse response = self.callAIService(request);

                    log.info("✅ AI 분석 응답 수신: gameId={}, gameSeq={}, aiStatus={}, description={}", 
                            detail.getGameId(), detail.getGameSeq(), response.getAiStatus(), response.getDescription());

                    // 4. 결과 처리
                    self.updateGameDetailWithAIResult(detail.getGameId(), detail.getGameSeq(), response);

                } catch (Exception e) {
                    log.error("❌ 개별 AI 분석 처리 중 오류: gameId={}, gameSeq={}", 
                            detail.getGameId(), detail.getGameSeq(), e);
                    
                    // 실패 처리
                    self.markGameDetailAsFailed(detail.getGameId(), detail.getGameSeq(), 
                                            "AI 분석 중 오류: " + e.getMessage());
                }
            } else {
                log.info("⏭️ AI 분석 불필요: gameId={}, gameSeq={}, 현재상태='{}', answerText='{}'", 
                        detail.getGameId(), detail.getGameSeq(), detail.getAiStatus(), detail.getAnswerText());
            }
        }

        log.info("=== 분석 대상 요약 ===");
        log.info("전체 디테일: {}, 분석 필요: {}", gameDetails.size(), needsAnalysisCount);

        // 5. 전체 게임 상태 업데이트
        log.info("게임 상태 업데이트 시작: gameId={}", gameId);
        updateGameStatusBasedOnDetails(gameId);
        log.info("게임 상태 업데이트 완료: gameId={}", gameId);
    }
        // AI 서비스 호출 (별도 트랜잭션)
        @Transactional(propagation = Propagation.REQUIRES_NEW)
        public AIAnalysisResponse callAIService(AIAnalysisRequest request) {
            return aiClientService.analyzeAnswer(request);
        }

        // 게임 디테일 AI 결과 업데이트 (별도 트랜잭션)
        @Transactional(propagation = Propagation.REQUIRES_NEW)
        public void updateGameDetailWithAIResult(String gameId, Integer gameSeq, AIAnalysisResponse response) {
            Optional<GameDetail> optionalDetail = gameDetailRepository.findByGameIdAndGameSeq(gameId, gameSeq);
            if (optionalDetail.isPresent()) {
                GameDetail detail = optionalDetail.get();
                
                if ("COMPLETED".equals(response.getAiStatus())) {
                    detail.updateAIAnalysisResult(
                        response.getWrongOption1(),
                        response.getWrongOption2(),
                        response.getWrongOption3(),
                        response.getWrongScore1(),
                        response.getWrongScore2(),
                        response.getWrongScore3(),
                        response.getAiStatus(),
                        response.getDescription()
                    );
                    log.info("AI 분석 성공 - DB 업데이트 완료: gameId={}, gameSeq={}", gameId, gameSeq);
                } else {
                    detail.markAIAnalysisFailed(response.getDescription());
                    log.warn("AI 분석 실패 처리: gameId={}, gameSeq={}, reason={}", gameId, gameSeq, response.getDescription());
                }
                
                gameDetailRepository.save(detail);
            }
    }

    // 게임 디테일 실패 처리 (별도 트랜잭션)
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void markGameDetailAsFailed(String gameId, Integer gameSeq, String errorMessage) {
        Optional<GameDetail> optionalDetail = gameDetailRepository.findByGameIdAndGameSeq(gameId, gameSeq);
        if (optionalDetail.isPresent()) {
            GameDetail detail = optionalDetail.get();
            detail.markAIAnalysisFailed(errorMessage);
            gameDetailRepository.save(detail);
        }
    }

    // 게임 실패 처리 (별도 트랜잭션)
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void markGameAsFailed(String gameId, String errorMessage) {
        try {
            GameMaster gameMaster = getGameById(gameId);
            gameMaster.setCreationStatusCode("FAILED");
            gameMaster.setUpdatedBy("SYSTEM_ERROR");
            gameMasterRepository.save(gameMaster);
            
            log.error("게임을 실패 상태로 변경: gameId={}, error={}", gameId, errorMessage);
        } catch (Exception e) {
            log.error("게임 실패 상태 변경 중 오류: gameId={}", gameId, e);
        }
    }

    @Override
    @Transactional
    public void markGamesForReprocessing(List<String> gameIds) {
        try {
            for (String gameId : gameIds) {
                List<GameDetail> gameDetails = gameDetailRepository.findByGameIdOrderByGameSeq(gameId);

                for (GameDetail detail : gameDetails) {
                    if ("FAILED".equals(detail.getAiStatus()) || "ERROR".equals(detail.getAiStatus())) {
                        detail.setAiStatus("PENDING");
                        detail.setDescription("재처리 대상으로 변경됨");
                        detail.setAiProcessedAt(null);
                        gameDetailRepository.save(detail);
                    }
                }
            }

            log.info("게임 재처리 표시 완료: {} 개", gameIds.size());

        } catch (Exception e) {
            log.error("게임 재처리 표시 실패: {}", e.getMessage());
            throw new RuntimeException("재처리 표시 실패", e);
        }
    }

    @Override
    @Transactional
    public void markGamesAsProcessing(List<String> gameIds) {
        try {
            for (String gameId : gameIds) {
                List<GameDetail> gameDetails = gameDetailRepository.findByGameIdOrderByGameSeq(gameId);

                for (GameDetail detail : gameDetails) {
                    if ("PENDING".equals(detail.getAiStatus())) {
                        detail.markAIAnalyzing();
                        gameDetailRepository.save(detail);
                    }
                }
            }

            log.info("게임 진행중 표시 완료: {} 개", gameIds.size());

        } catch (Exception e) {
            log.error("게임 진행중 표시 실패: {}", e.getMessage());
            throw new RuntimeException("진행중 표시 실패", e);
        }
    }

    @Override
    @Transactional
    public void markGamesAsCompleted(List<String> gameIds) {
        try {
            for (String gameId : gameIds) {
                List<GameDetail> gameDetails = gameDetailRepository.findByGameIdOrderByGameSeq(gameId);

                for (GameDetail detail : gameDetails) {
                    if ("PROCESSING".equals(detail.getAiStatus()) || "ANALYZING".equals(detail.getAiStatus())) {
                        detail.setAiStatus("COMPLETED");
                        detail.setDescription("AI 분석 완료");
                        gameDetailRepository.save(detail);
                    }
                }

                // 게임 마스터 상태도 업데이트
                GameMaster gameMaster = gameMasterRepository.findById(gameId).orElse(null);
                if (gameMaster != null) {
                    gameMaster.setCreationStatusCode("COMPLETED");
                    gameMasterRepository.save(gameMaster);
                }
            }

            log.info("게임 완료 표시 완료: {} 개", gameIds.size());

        } catch (Exception e) {
            log.error("게임 완료 표시 실패: {}", e.getMessage());
            throw new RuntimeException("완료 표시 실패", e);
        }
    }

    @Override
    @Transactional
    public void markGamesAsError(List<String> gameIds, String errorDescription) {
        try {
            for (String gameId : gameIds) {
                List<GameDetail> gameDetails = gameDetailRepository.findByGameIdOrderByGameSeq(gameId);

                for (GameDetail detail : gameDetails) {
                    detail.markAIAnalysisFailed(errorDescription != null ? errorDescription : "처리 중 오류 발생");
                    gameDetailRepository.save(detail);
                }

                // 게임 마스터 상태도 업데이트
                GameMaster gameMaster = gameMasterRepository.findById(gameId).orElse(null);
                if (gameMaster != null) {
                    gameMaster.setCreationStatusCode("FAILED");
                    gameMasterRepository.save(gameMaster);
                }
            }

            log.info("게임 오류 표시 완료: {} 개", gameIds.size());

        } catch (Exception e) {
            log.error("게임 오류 표시 실패: {}", e.getMessage());
            throw new RuntimeException("오류 표시 실패", e);
        }
    }

    @Override
    @Transactional(readOnly = true)
    public List<GameMaster> getGamesByGameName(String gameName) {
        return gameMasterRepository.findByGameNameContaining(gameName);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<GameMaster> getGamesByGameId(String gameId) {
        return gameMasterRepository.findByGameId(gameId);
    }

    @Override
    public String requestBatchAnalysisByDifficulty(String difficulty, int limit) {
        return aiClientService.requestBatchAnalysisByDifficulty(difficulty, limit);
    }

    @Override
    @Transactional(readOnly = true)
    public Map<String, Object> getProcessingStatistics() {
        try {
            Map<String, Object> statistics = new HashMap<>();

            // 전체 통계
            Map<String, Long> totalStats = countByAiStatusGrouped();
            statistics.put("total", totalStats);

            // 난이도별 통계
            Map<String, Map<String, Long>> difficultyStats = new HashMap<>();

            for (String difficultyCode : Arrays.asList("D10001", "D10002", "D10003", "D10004")) {
                String difficulty = mapDifficultyCodeToLevel(difficultyCode);
                Map<String, Long> stats = countByAiStatusAndDifficultyGrouped(difficultyCode);
                difficultyStats.put(difficulty, stats);
            }

            statistics.put("byDifficulty", difficultyStats);

            // 최근 처리 현황 (24시간 이내)
            LocalDateTime yesterday = LocalDateTime.now().minusDays(1);
            Long recentProcessed = gameDetailRepository.countRecentlyProcessed(yesterday);
            statistics.put("recentProcessed", recentProcessed);

            return statistics;

        } catch (Exception e) {
            log.error("통계 조회 실패: {}", e.getMessage());
            throw new RuntimeException("통계 조회 실패", e);
        }
    }

    // Private 헬퍼 메서드들
    @Transactional
    private void updateGameStatusBasedOnDetails(String gameId) {
        List<GameDetail> gameDetails = gameDetailRepository.findByGameIdOrderByGameOrder(gameId);

        boolean allCompleted = gameDetails.stream()
                .filter(detail -> detail.getAnswerText() != null && !detail.getAnswerText().trim().isEmpty())
                .allMatch(GameDetail::isAIAnalysisCompleted);

        if (allCompleted && !gameDetails.isEmpty()) {
            updateGameStatus(gameId, "COMPLETED", "SYSTEM");
        }
    }

    private String generateGameId() {
        String dateStr = LocalDate.now().format(DateTimeFormatter.ofPattern("yyMMdd"));
        String maxGameId = gameMasterRepository.findMaxGameIdByDate(dateStr);

        int nextSeq = 1;
        if (maxGameId != null && maxGameId.length() >= 10) {
            String seqStr = maxGameId.substring(7);
            nextSeq = Integer.parseInt(seqStr) + 1;
        }

        return String.format("G%s%03d", dateStr, nextSeq);
    }

    @Transactional(readOnly = true)
    private Map<String, Long> countByAiStatusGrouped() {
        List<Object[]> results = gameDetailRepository.findAiStatusCounts();
        Map<String, Long> statusCounts = new HashMap<>();

        for (Object[] result : results) {
            String status = (String) result[0];
            Long count = (Long) result[1];
            statusCounts.put(status, count);
        }

        return statusCounts;
    }

    @Transactional(readOnly = true)
    private Map<String, Long> countByAiStatusAndDifficultyGrouped(String difficultyCode) {
        List<Object[]> results = gameDetailRepository.findAiStatusCountsByDifficulty(difficultyCode);
        Map<String, Long> statusCounts = new HashMap<>();

        for (Object[] result : results) {
            String status = (String) result[0];
            Long count = (Long) result[1];
            statusCounts.put(status, count);
        }

        return statusCounts;
    }
}