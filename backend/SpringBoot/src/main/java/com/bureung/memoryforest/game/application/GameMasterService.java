package com.bureung.memoryforest.game.application;

import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

import com.bureung.memoryforest.game.domain.GameMaster;

/**
 * 게임 마스터 관리 서비스 인터페이스
 */
public interface GameMasterService {
    GameMaster getGameById(String gameId);
    GameMaster saveGame(GameMaster gameMaster);
    List<GameMaster> getAllGames();
    List<GameMaster> getGamesByDifficultyLevel(String difficultyLevel);
    List<GameMaster> getGamesByCreationStatusCode(String creationStatusCode);
    List<GameMaster> getGamesByCreatedBy(String createdBy);
    String createNewGame(String gameName, String gameDesc, Integer gameCount,
                         String difficultyLevel, String createdBy);
    void updateGameStatus(String gameId, String statusCode, String updatedBy);
    List<GameMaster> getGamesNeedingAIAnalysis();
    List<GameMaster> getGamesByAIStatus(String aiStatus);
    CompletableFuture<Void> processAIAnalysis(String gameId);
    void markGamesForReprocessing(List<String> gameIds);
    void markGamesAsProcessing(List<String> gameIds);
    void markGamesAsCompleted(List<String> gameIds);
    void markGamesAsError(List<String> gameIds, String errorDescription);
    String requestBatchAnalysisByDifficulty(String difficulty, int limit);
    Map<String, Object> getProcessingStatistics();
}
