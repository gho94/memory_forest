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
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.concurrent.CompletableFuture;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class GameMasterServiceImpl implements GameMasterService {

    private final GameMasterRepository gameMasterRepository;
    private final GameDetailRepository gameDetailRepository;
    private final AIClientService aiClientService;

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
        return gameMasterRepository.findByDifficultyLevelOrderByCreatedAtDesc(difficultyLevel);
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
                .difficultyLevel(difficultyLevel)
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
    public List<GameMaster> getGamesNeedingAIAnalysis() {
        // GameDetail에서 AI 분석이 필요한 게임들의 gameId를 가져와서 
        // GameMaster와 매치하는 로직
        List<GameDetail> pendingDetails = gameDetailRepository.findPendingAIAnalysis();
        
        return pendingDetails.stream()
                .map(detail -> getGameById(detail.getGameId()))
                .distinct()
                .toList();
    }

    @Override
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
            // 해당 게임의 모든 GameDetail 조회
            List<GameDetail> gameDetails = gameDetailRepository.findByGameIdOrderByGameOrder(gameId);
            
            for (GameDetail detail : gameDetails) {
                if (detail.needsAIAnalysis()) {
                    // AI 분석 요청
                    AIAnalysisRequest request = new AIAnalysisRequest();
                    request.setGameId(detail.getGameId());
                    request.setGameSeq(detail.getGameSeq());
                    request.setAnswerText(detail.getAnswerText());
                    
                    detail.markAIAnalyzing();
                    gameDetailRepository.save(detail);
                    
                    AIAnalysisResponse response = aiClientService.analyzeAnswer(request);
                    
                    if ("COMPLETED".equals(response.getAiStatus())) {
                        detail.updateAIAnalysisResult(
                            response.getWrongOption1(),
                            response.getWrongOption2(), 
                            response.getWrongOption3(),
                            response.getSimilarityScore1(),
                            response.getSimilarityScore2(),
                            response.getSimilarityScore3(),
                            response.getAiStatus(),
                            response.getDescription()
                        );
                    } else {
                        detail.markAIAnalysisFailed(response.getDescription());
                    }
                    
                    gameDetailRepository.save(detail);
                }
            }
            
            // 모든 GameDetail의 AI 분석이 완료되면 GameMaster 상태도 업데이트
            updateGameStatusBasedOnDetails(gameId);
            
        } catch (Exception e) {
            log.error("AI 분석 처리 중 오류: gameId={}", gameId, e);
        }
        
        return CompletableFuture.completedFuture(null);
    }

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
}