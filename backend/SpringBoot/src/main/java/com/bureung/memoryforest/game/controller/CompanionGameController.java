package com.bureung.memoryforest.game.controller;

import com.bureung.memoryforest.game.application.GameMasterService;
import com.bureung.memoryforest.game.domain.GameMaster;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import lombok.Getter;
import lombok.Setter;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/companion/game")
@RequiredArgsConstructor
public class CompanionGameController {
    
    private final GameMasterService gameMasterService;

    // 특정 게임 조회
    @GetMapping("/{gameId}")
    public ResponseEntity<GameMaster> getGame(@PathVariable String gameId) {
        log.info("게임 조회: gameId={}", gameId);
        return ResponseEntity.ok(gameMasterService.getGameById(gameId));
    }

    // 난이도별 게임 조회
    @GetMapping("/difficulty/{difficultyLevel}")
    public ResponseEntity<List<GameMaster>> getGamesByDifficulty(@PathVariable String difficultyLevel) {
        log.info("난이도별 게임 조회: difficultyLevel={}", difficultyLevel);
        return ResponseEntity.ok(gameMasterService.getGamesByDifficultyLevel(difficultyLevel));
    }

    // 모든 게임 조회
    @GetMapping("/all")
    public ResponseEntity<List<GameMaster>> getAllGames() {
        return ResponseEntity.ok(gameMasterService.getAllGames());
    }

    // 생성자별 게임 조회
    @GetMapping("/creator/{createdBy}")
    public ResponseEntity<List<GameMaster>> getGamesByCreatedBy(@PathVariable String createdBy) {
        return ResponseEntity.ok(gameMasterService.getGamesByCreatedBy(createdBy));
    }

    // 게임 생성 상태별 조회
    @GetMapping("/status/{creationStatusCode}")
    public ResponseEntity<List<GameMaster>> getGamesByStatus(@PathVariable String creationStatusCode) {
        return ResponseEntity.ok(gameMasterService.getGamesByCreationStatusCode(creationStatusCode));
    }

    // 새 게임 생성
    @PostMapping("/create")
    public ResponseEntity<Map<String, String>> createGame(@RequestBody CreateGameRequest request) {
        try {
            String gameId = gameMasterService.createNewGame(
                request.getGameName(),
                request.getGameDesc(),
                request.getGameCount(),
                request.getDifficultyLevel(),
                request.getCreatedBy()
            );
            
            return ResponseEntity.ok(Map.of(
                "message", "게임이 생성되었습니다.",
                "gameId", gameId
            ));
        } catch (Exception e) {
            log.error("게임 생성 실패", e);
            return ResponseEntity.badRequest()
                .body(Map.of("error", "게임 생성 실패: " + e.getMessage()));
        }
    }

    // 게임 상태 업데이트
    @PutMapping("/{gameId}/status")
    public ResponseEntity<Map<String, String>> updateGameStatus(
            @PathVariable String gameId,
            @RequestBody UpdateStatusRequest request) {
        try {
            gameMasterService.updateGameStatus(gameId, request.getStatusCode(), request.getUpdatedBy());
            return ResponseEntity.ok(Map.of(
                "message", "게임 상태가 업데이트되었습니다.",
                "gameId", gameId,
                "status", request.getStatusCode()
            ));
        } catch (Exception e) {
            log.error("게임 상태 업데이트 실패: gameId={}", gameId, e);
            return ResponseEntity.badRequest()
                .body(Map.of("error", "상태 업데이트 실패: " + e.getMessage()));
        }
    }

    // AI 분석 시작
    @PostMapping("/{gameId}/analyze")
    public ResponseEntity<Map<String, String>> analyzeGame(@PathVariable String gameId) {
        try {
            gameMasterService.processAIAnalysis(gameId);
            return ResponseEntity.ok(Map.of(
                "message", "AI 분석이 시작되었습니다.",
                "gameId", gameId
            ));
        } catch (Exception e) {
            log.error("AI 분석 요청 실패: gameId={}", gameId, e);
            return ResponseEntity.badRequest()
                .body(Map.of("error", "AI 분석 요청 실패: " + e.getMessage()));
        }
    }

    // AI 분석이 필요한 모든 게임 배치 분석
    @PostMapping("/analyze/batch")
    public ResponseEntity<Map<String, Object>> batchAnalyze() {
        try {
            List<GameMaster> needingAnalysis = gameMasterService.getGamesNeedingAIAnalysis();

            int successCount = 0;
            int failCount = 0;

            for (GameMaster game : needingAnalysis) {
                try {
                    gameMasterService.processAIAnalysis(game.getGameId());
                    successCount++;
                } catch (Exception e) {
                    log.error("게임 AI 분석 실패: gameId={}", game.getGameId(), e);
                    failCount++;
                }
            }

            return ResponseEntity.ok(Map.of(
                "message", "배치 AI 분석 완료",
                "totalGames", needingAnalysis.size(),
                "successCount", successCount,
                "failCount", failCount
            ));

        } catch (Exception e) {
            log.error("배치 AI 분석 실패", e);
            return ResponseEntity.badRequest()
                .body(Map.of("error", "배치 AI 분석 실패: " + e.getMessage()));
        }
    }

    // AI 분석 상태 정보
    @GetMapping("/analysis/status")
    public ResponseEntity<Map<String, Object>> getAnalysisStatus() {
        List<GameMaster> needingAnalysis = gameMasterService.getGamesNeedingAIAnalysis();
        List<GameMaster> allGames = gameMasterService.getAllGames();
        List<GameMaster> completedGames = gameMasterService.getGamesByAIStatus("COMPLETED");
        List<GameMaster> failedGames = gameMasterService.getGamesByAIStatus("FAILED");

        return ResponseEntity.ok(Map.of(
            "totalGames", allGames.size(),
            "needingAnalysis", needingAnalysis.size(),
            "completed", completedGames.size(),
            "failed", failedGames.size(),
            "gamesNeedingAnalysis", needingAnalysis
        ));
    }

    // AI 상태별 게임 조회
    @GetMapping("/analysis/status/{aiStatus}")
    public ResponseEntity<List<GameMaster>> getGamesByAIStatus(@PathVariable String aiStatus) {
        return ResponseEntity.ok(gameMasterService.getGamesByAIStatus(aiStatus));
    }

    // DTO 클래스들
    @Getter
    @Setter
    public static class CreateGameRequest {
        private String gameName;
        private String gameDesc;
        private Integer gameCount;
        private String difficultyLevel;
        private String createdBy;
    }

    @Getter
    @Setter
    public static class UpdateStatusRequest {
        private String statusCode;
        private String updatedBy;
    }
}