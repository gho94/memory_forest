// GameStatusController.java - 게임 상태 관리 컨트롤러
package com.bureung.memoryforest.game.controller;

import com.bureung.memoryforest.ai.AIClientService;
import com.bureung.memoryforest.game.application.GameMasterService;
import com.bureung.memoryforest.game.dto.request.UpdateStatusRequestDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/games/status")
@RequiredArgsConstructor
@Slf4j
public class GameStatusController {

    private final GameMasterService gameMasterService;
    private final AIClientService aiClientService;

    /**
     * 게임 상태 일괄 업데이트 (Airflow에서 호출)
     */
    @PostMapping("/batch-update")
    public ResponseEntity<?> batchUpdateStatus(@RequestBody UpdateStatusRequestDto request) {
        try {
            log.info("게임 상태 일괄 업데이트 요청: {}", request);
            
            // 상태별 처리 로직
            switch (request.getTargetStatus()) {
                case "PENDING":
                    // 대기 상태로 변경 (재처리 대상)
                    gameMasterService.markGamesForReprocessing(request.getGameIds());
                    break;
                    
                case "PROCESSING":
                    // 진행 중 상태로 변경
                    gameMasterService.markGamesAsProcessing(request.getGameIds());
                    break;
                    
                case "COMPLETED":
                    // 완료 상태로 변경
                    gameMasterService.markGamesAsCompleted(request.getGameIds());
                    break;
                    
                case "ERROR":
                    // 오류 상태로 변경
                    gameMasterService.markGamesAsError(request.getGameIds(), request.getDescription());
                    break;
                    
                default:
                    return ResponseEntity.badRequest()
                            .body(Map.of("error", "지원하지 않는 상태: " + request.getTargetStatus()));
            }
            
            return ResponseEntity.ok(Map.of(
                    "message", "상태 업데이트 완료",
                    "updatedCount", request.getGameIds().size(),
                    "targetStatus", request.getTargetStatus()
            ));
            
        } catch (Exception e) {
            log.error("게임 상태 일괄 업데이트 실패: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "상태 업데이트 실패: " + e.getMessage()));
        }
    }

    /**
     * 난이도별 배치 분석 요청
     */
    @PostMapping("/batch-analyze/{difficulty}")
    public ResponseEntity<?> requestBatchAnalysisByDifficulty(
            @PathVariable String difficulty,
            @RequestParam(defaultValue = "50") int limit) {
        try {
            log.info("난이도별 배치 분석 요청: difficulty={}, limit={}", difficulty, limit);
            
            String result = aiClientService.requestBatchAnalysisByDifficulty(difficulty, limit);
            
            return ResponseEntity.ok(Map.of(
                    "message", "배치 분석 요청 완료",
                    "difficulty", difficulty,
                    "limit", limit,
                    "result", result
            ));
            
        } catch (Exception e) {
            log.error("난이도별 배치 분석 요청 실패: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "배치 분석 요청 실패: " + e.getMessage()));
        }
    }

    /**
     * AI 모델 상태 조회
     */
    @GetMapping("/ai-models")
    public ResponseEntity<?> getAIModelsStatus() {
        try {
            String modelsStatus = aiClientService.getModelsStatus();
            return ResponseEntity.ok(modelsStatus);
        } catch (Exception e) {
            log.error("AI 모델 상태 조회 실패: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "모델 상태 조회 실패: " + e.getMessage()));
        }
    }

    /**
     * 특정 난이도 모델 리로드
     */
    @PostMapping("/ai-models/reload/{difficulty}")
    public ResponseEntity<?> reloadDifficultyModel(@PathVariable String difficulty) {
        try {
            String result = aiClientService.reloadDifficultyModel(difficulty);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("모델 리로드 실패: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "모델 리로드 실패: " + e.getMessage()));
        }
    }

    /**
     * 게임 처리 통계 조회
     */
    @GetMapping("/statistics")
    public ResponseEntity<?> getProcessingStatistics() {
        try {
            // 통계 조회 로직 구현
            Map<String, Object> statistics = gameMasterService.getProcessingStatistics();
            return ResponseEntity.ok(statistics);
        } catch (Exception e) {
            log.error("통계 조회 실패: {}", e.getMessage());
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "통계 조회 실패: " + e.getMessage()));
        }
    }
}