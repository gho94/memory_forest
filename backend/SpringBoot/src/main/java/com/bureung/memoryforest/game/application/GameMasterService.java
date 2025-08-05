package com.bureung.memoryforest.game.application;

import com.bureung.memoryforest.game.domain.GameMaster;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

public interface GameMasterService {
    // 기본 CRUD
    GameMaster getGameById(String gameId);
    GameMaster saveGame(GameMaster gameMaster);
    List<GameMaster> getAllGames();
    
    // 난이도별 조회
    List<GameMaster> getGamesByDifficultyLevel(String difficultyLevel);
    
    // 상태별 조회
    List<GameMaster> getGamesByCreationStatusCode(String creationStatusCode);
    
    // 생성자별 조회
    List<GameMaster> getGamesByCreatedBy(String createdBy);
    
    // 새로운 게임 생성
    String createNewGame(String gameName, String gameDesc, Integer gameCount,
                        String difficultyLevel, String createdBy);
    
    // 게임 상태 업데이트
    void updateGameStatus(String gameId, String statusCode, String updatedBy);
    
    // AI 분석 관련
    List<GameMaster> getGamesNeedingAIAnalysis();
    List<GameMaster> getGamesByAIStatus(String aiStatus);
    CompletableFuture<Void> processAIAnalysis(String gameId);
    
    // 상태 관리 메서드들
    void markGamesForReprocessing(List<String> gameIds);
    void markGamesAsProcessing(List<String> gameIds);
    void markGamesAsCompleted(List<String> gameIds);
    void markGamesAsError(List<String> gameIds, String errorDescription);
    
    // 난이도별 배치 분석 요청
    String requestBatchAnalysisByDifficulty(String difficulty, int limit);
    
    // 처리 통계 조회
    Map<String, Object> getProcessingStatistics();
}