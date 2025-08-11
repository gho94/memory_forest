package com.bureung.memoryforest.game.controller;

import com.bureung.memoryforest.game.application.GameMasterService;
import com.bureung.memoryforest.game.application.GameQueryService;
import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.game.dto.request.GameCreateRequestDto;
import com.bureung.memoryforest.game.dto.request.GameDashboardRequestDto;
import com.bureung.memoryforest.game.dto.request.UpdateStatusRequestDto;
import com.bureung.memoryforest.game.dto.response.GameDashboardResponseDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
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
    private final GameQueryService gameQueryService;

    /**
     * 게임 단건 조회
     */
    @GetMapping("/{gameId}")
    public ResponseEntity<GameMaster> getGame(@PathVariable String gameId) {
        log.info("게임 조회: gameId={}", gameId);
        try {
            GameMaster game = gameMasterService.getGameById(gameId);
            return ResponseEntity.ok(game);
        } catch (Exception e) {
            log.error("게임 조회 실패: gameId={}", gameId, e);
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * 난이도별 게임 조회
     */
    @GetMapping("/difficulty/{difficultyLevel}")
    public ResponseEntity<List<GameMaster>> getGamesByDifficulty(@PathVariable String difficultyLevel) {
        log.info("난이도별 게임 조회: difficultyLevel={}", difficultyLevel);
        try {
            List<GameMaster> games = gameMasterService.getGamesByDifficultyLevel(difficultyLevel);
            return ResponseEntity.ok(games);
        } catch (Exception e) {
            log.error("난이도별 게임 조회 실패: difficultyLevel={}", difficultyLevel, e);
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * 전체 게임 조회
     */
    @GetMapping("/all")
    public ResponseEntity<List<GameMaster>> getAllGames() {
        try {
            List<GameMaster> games = gameMasterService.getAllGames();
            return ResponseEntity.ok(games);
        } catch (Exception e) {
            log.error("전체 게임 조회 실패", e);
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * 생성자별 게임 조회
     */
    @GetMapping("/creator/{createdBy}")
    public ResponseEntity<List<GameMaster>> getGamesByCreatedBy(@PathVariable String createdBy) {
        try {
            List<GameMaster> games = gameMasterService.getGamesByCreatedBy(createdBy);
            return ResponseEntity.ok(games);
        } catch (Exception e) {
            log.error("생성자별 게임 조회 실패: createdBy={}", createdBy, e);
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * 상태별 게임 조회
     */
    @GetMapping("/status/{creationStatusCode}")
    public ResponseEntity<List<GameMaster>> getGamesByStatus(@PathVariable String creationStatusCode) {
        try {
            List<GameMaster> games = gameMasterService.getGamesByCreationStatusCode(creationStatusCode);
            return ResponseEntity.ok(games);
        } catch (Exception e) {
            log.error("상태별 게임 조회 실패: status={}", creationStatusCode, e);
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * 게임 생성
     */
    @PostMapping("/create")
    public ResponseEntity<Map<String, String>> createGame(@RequestBody GameCreateRequestDto request) {
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

    /**
     * 게임 상태 업데이트
     */
    @PutMapping("/{gameId}/status")
    public ResponseEntity<Map<String, String>> updateGameStatus(
            @PathVariable String gameId,
            @RequestBody UpdateStatusRequestDto request) {
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

    /**
     * 단일 게임 AI 분석 요청
     */
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

    /**
     * 배치 AI 분석 요청
     */
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

    /**
     * 난이도별 배치 AI 분석 요청
     */
    @PostMapping("/analyze/batch/{difficulty}")
    public ResponseEntity<Map<String, String>> batchAnalyzeByDifficulty(
            @PathVariable String difficulty,
            @RequestParam(defaultValue = "10") int limit) {
        try {
            String batchId = gameMasterService.requestBatchAnalysisByDifficulty(difficulty, limit);
            return ResponseEntity.ok(Map.of(
                "message", "난이도별 배치 AI 분석이 시작되었습니다.",
                "difficulty", difficulty,
                "limit", String.valueOf(limit),
                "batchId", batchId
            ));
        } catch (Exception e) {
            log.error("난이도별 배치 AI 분석 실패: difficulty={}", difficulty, e);
            return ResponseEntity.badRequest()
                .body(Map.of("error", "배치 AI 분석 실패: " + e.getMessage()));
        }
    }

    /**
     * AI 분석 상태 조회
     */
    @GetMapping("/analysis/status")
    public ResponseEntity<Map<String, Object>> getAnalysisStatus() {
        try {
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
        } catch (Exception e) {
            log.error("분석 상태 조회 실패", e);
            return ResponseEntity.badRequest()
                .body(Map.of("error", "분석 상태 조회 실패: " + e.getMessage()));
        }
    }

    /**
     * AI 상태별 게임 조회
     */
    @GetMapping("/analysis/status/{aiStatus}")
    public ResponseEntity<List<GameMaster>> getGamesByAIStatus(@PathVariable String aiStatus) {
        try {
            List<GameMaster> games = gameMasterService.getGamesByAIStatus(aiStatus);
            return ResponseEntity.ok(games);
        } catch (Exception e) {
            log.error("AI 상태별 게임 조회 실패: aiStatus={}", aiStatus, e);
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * 처리 통계 조회
     */
    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getProcessingStatistics() {
        try {
            Map<String, Object> statistics = gameMasterService.getProcessingStatistics();
            return ResponseEntity.ok(statistics);
        } catch (Exception e) {
            log.error("처리 통계 조회 실패", e);
            return ResponseEntity.badRequest()
                .body(Map.of("error", "통계 조회 실패: " + e.getMessage()));
        }
    }

    /**
     * 게임 재처리 요청
     */
    @PostMapping("/reprocess")
    public ResponseEntity<Map<String, String>> reprocessGames(@RequestBody List<String> gameIds) {
        try {
            gameMasterService.markGamesForReprocessing(gameIds);
            return ResponseEntity.ok(Map.of(
                "message", "게임 재처리 요청이 완료되었습니다.",
                "count", String.valueOf(gameIds.size())
            ));
        } catch (Exception e) {
            log.error("게임 재처리 요청 실패", e);
            return ResponseEntity.badRequest()
                .body(Map.of("error", "재처리 요청 실패: " + e.getMessage()));
        }
    }

    /**
     * 게임 상태 일괄 변경 (진행중으로)
     */
    @PostMapping("/batch/processing")
    public ResponseEntity<Map<String, String>> markGamesAsProcessing(@RequestBody List<String> gameIds) {
        try {
            gameMasterService.markGamesAsProcessing(gameIds);
            return ResponseEntity.ok(Map.of(
                "message", "게임 상태가 진행중으로 변경되었습니다.",
                "count", String.valueOf(gameIds.size())
            ));
        } catch (Exception e) {
            log.error("게임 진행중 상태 변경 실패", e);
            return ResponseEntity.badRequest()
                .body(Map.of("error", "상태 변경 실패: " + e.getMessage()));
        }
    }

    /**
     * 게임 상태 일괄 변경 (완료로)
     */
    @PostMapping("/batch/completed")
    public ResponseEntity<Map<String, String>> markGamesAsCompleted(@RequestBody List<String> gameIds) {
        try {
            gameMasterService.markGamesAsCompleted(gameIds);
            return ResponseEntity.ok(Map.of(
                "message", "게임 상태가 완료로 변경되었습니다.",
                "count", String.valueOf(gameIds.size())
            ));
        } catch (Exception e) {
            log.error("게임 완료 상태 변경 실패", e);
            return ResponseEntity.badRequest()
                .body(Map.of("error", "상태 변경 실패: " + e.getMessage()));
        }
    }

    /**
     * 게임 상태 일괄 변경 (오류로)
     */
    @PostMapping("/batch/error")
    public ResponseEntity<Map<String, String>> markGamesAsError(
            @RequestBody Map<String, Object> request) {
        try {
            @SuppressWarnings("unchecked")
            List<String> gameIds = (List<String>) request.get("gameIds");
            String errorDescription = (String) request.get("errorDescription");
            
            gameMasterService.markGamesAsError(gameIds, errorDescription);
            return ResponseEntity.ok(Map.of(
                "message", "게임 상태가 오류로 변경되었습니다.",
                "count", String.valueOf(gameIds.size())
            ));
        } catch (Exception e) {
            log.error("게임 오류 상태 변경 실패", e);
            return ResponseEntity.badRequest()
                .body(Map.of("error", "상태 변경 실패: " + e.getMessage()));
        }
    }

    @GetMapping("/dashboard")
    public ResponseEntity<GameDashboardResponseDto> getDashboard(GameDashboardRequestDto request) {
        GameDashboardResponseDto response = gameQueryService.getDashboardStats(request);
        return ResponseEntity.ok(response);
    }
}