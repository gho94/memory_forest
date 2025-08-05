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
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class GameMasterServiceImpl implements GameMasterService {

    private final GameMasterRepository gameMasterRepository;
    private final GameDetailRepository gameDetailRepository;
    private final AIClientService aiClientService;
    
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

    @Override
    @Async("aiTaskExecutor")
    public CompletableFuture<Void> processAIAnalysis(String gameId) {
        try {
            List<GameDetail> gameDetails = gameDetailRepository.findByGameIdOrderByGameOrder(gameId);

            for (GameDetail detail : gameDetails) {
                if (detail.needsAIAnalysis()) {
                    log.info("AI 분석 요청 시작: gameId={}, gameSeq={}, answerText={}",
                            detail.getGameId(), detail.getGameSeq(), detail.getAnswerText());

                    AIAnalysisRequest request = new AIAnalysisRequest();
                    request.setGameId(detail.getGameId());
                    request.setGameSeq(detail.getGameSeq());
                    request.setAnswerText(detail.getAnswerText());

                    detail.markAIAnalyzing();
                    gameDetailRepository.save(detail);

                    AIAnalysisResponse response = aiClientService.analyzeAnswer(request);

                    log.info("AI 분석 응답: gameId={}, gameSeq={}, aiStatus={}, description={}",
                            detail.getGameId(), detail.getGameSeq(), response.getAiStatus(), response.getDescription());

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
                        log.info("AI 분석 결과 DB 업데이트 완료: gameId={}, gameSeq={}", detail.getGameId(), detail.getGameSeq());
                    } else {
                        detail.markAIAnalysisFailed(response.getDescription());
                        log.warn("AI 분석 실패 처리: gameId={}, gameSeq={}, reason={}", detail.getGameId(), detail.getGameSeq(), response.getDescription());
                    }

                    gameDetailRepository.save(detail);
                }
            }

            updateGameStatusBasedOnDetails(gameId);
            log.info("게임 상태 업데이트 완료 후 processAIAnalysis 종료: gameId={}", gameId);

        } catch (Exception e) {
            log.error("AI 분석 처리 중 오류: gameId={}", gameId, e);
        }

        return CompletableFuture.completedFuture(null);
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