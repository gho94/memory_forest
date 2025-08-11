package com.bureung.memoryforest.test.controller;

import com.bureung.memoryforest.ai.AIAnalysisRequest;
import com.bureung.memoryforest.ai.AIAnalysisResponse;
import com.bureung.memoryforest.ai.AIClientService;
import com.bureung.memoryforest.game.domain.GameDetail;
import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.game.repository.GameDetailRepository;
import com.bureung.memoryforest.game.repository.GameMasterRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.Optional;

@Slf4j
@RestController
@RequestMapping("/api/test")
@RequiredArgsConstructor
public class TestController {

    private final AIClientService aiClientService;
    private final GameDetailRepository gameDetailRepository;
    private final GameMasterRepository gameMasterRepository;

    /**
     * FastAPI 연결 테스트
     */
    @GetMapping("/fastapi/health")
    public ResponseEntity<Map<String, String>> testFastAPIHealth() {
        try {
            boolean isHealthy = aiClientService.isHealthy();
            return ResponseEntity.ok(Map.of(
                "status", isHealthy ? "success" : "error",
                "message", isHealthy ? "FastAPI 연결 성공" : "FastAPI 연결 실패"
            ));
        } catch (Exception e) {
            log.error("FastAPI health check 실패", e);
            return ResponseEntity.ok(Map.of(
                "status", "error",
                "message", "FastAPI 연결 실패: " + e.getMessage()
            ));
        }
    }

    /**
     * AI 분석 테스트 - 직접 요청
     */
    @PostMapping("/ai/analyze")
    public ResponseEntity<AIAnalysisResponse> testAIAnalysis(@RequestBody Map<String, Object> request) {
        try {
            String gameId = (String) request.get("gameId");
            Integer gameSeq = (Integer) request.get("gameSeq");
            String answerText = (String) request.get("answerText");
            String difficultyLevel = (String) request.getOrDefault("difficultyLevel", "NORMAL");

            log.info("AI 분석 테스트 요청: gameId={}, gameSeq={}, answerText={}, difficulty={}", 
                    gameId, gameSeq, answerText, difficultyLevel);

            AIAnalysisResponse response = aiClientService.analyzeAnswerWithDifficulty(
                gameId, gameSeq, answerText, difficultyLevel);

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            log.error("AI 분석 테스트 실패", e);
            
            AIAnalysisResponse errorResponse = new AIAnalysisResponse();
            errorResponse.setGameId((String) request.get("gameId"));
            errorResponse.setGameSeq((Integer) request.get("gameSeq"));
            errorResponse.setAiStatus("FAILED");
            errorResponse.setDescription("테스트 실패: " + e.getMessage());
            
            return ResponseEntity.ok(errorResponse);
        }
    }

    /**
     * 게임 데이터를 이용한 AI 분석 테스트
     */
    @PostMapping("/game/{gameId}/{gameSeq}/analyze")
    public ResponseEntity<Object> testGameAIAnalysis(
            @PathVariable String gameId,
            @PathVariable Integer gameSeq) {
        try {
            // GameDetail에서 답변 텍스트 조회
            Optional<GameDetail> gameDetailOpt = gameDetailRepository.findByGameIdAndGameSeq(gameId, gameSeq);
            
            if (gameDetailOpt.isEmpty()) {
                return ResponseEntity.ok(Map.of(
                    "status", "error",
                    "message", "게임 데이터를 찾을 수 없습니다: " + gameId + "/" + gameSeq
                ));
            }

            GameDetail gameDetail = gameDetailOpt.get();
            
            if (gameDetail.getAnswerText() == null || gameDetail.getAnswerText().trim().isEmpty()) {
                return ResponseEntity.ok(Map.of(
                    "status", "error",
                    "message", "답변 텍스트가 없습니다"
                ));
            }

            // 게임의 난이도 정보 조회
            GameMaster gameMaster = gameMasterRepository.findById(gameId).orElse(null);
            String difficultyLevel = "NORMAL";
            if (gameMaster != null) {
                difficultyLevel = mapDifficultyCodeToLevel(gameMaster.getDifficultyLevelCode());
            }

            log.info("게임 AI 분석 테스트: gameId={}, gameSeq={}, answerText={}, difficulty={}", 
                    gameId, gameSeq, gameDetail.getAnswerText(), difficultyLevel);

            // AI 분석 요청 (FastAPI가 자동으로 DB 저장)
            AIAnalysisResponse response = aiClientService.analyzeAnswerWithDifficulty(
                gameId, gameSeq, gameDetail.getAnswerText(), difficultyLevel);

            // FastAPI가 이미 DB에 저장했으므로 GameDetail 객체만 동기화
            if ("COMPLETED".equals(response.getAiStatus())) {
                gameDetail.updateAIAnalysisResult(
                    response.getWrongOption1(),
                    response.getWrongOption2(), 
                    response.getWrongOption3(),
                    response.getWrongScore1() != null ? response.getWrongScore1().intValue() : 0,
                    response.getWrongScore2() != null ? response.getWrongScore2().intValue() : 0,
                    response.getWrongScore3() != null ? response.getWrongScore3().intValue() : 0,
                    "B20007", // 완료 상태 코드
                    response.getDescription()
                );
                gameDetailRepository.save(gameDetail);
                
                log.info("AI 분석 결과 로컬 동기화 완료: gameId={}, gameSeq={}", gameId, gameSeq);
            } else if ("FAILED".equals(response.getAiStatus())) {
                gameDetail.markAIAnalysisFailed(response.getDescription());
                gameDetailRepository.save(gameDetail);
                
                log.warn("AI 분석 실패 처리: gameId={}, gameSeq={}", gameId, gameSeq);
            }

            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "AI 분석 완료 (FastAPI에서 DB 저장 완료)",
                "aiResponse", response,
                "gameDetail", gameDetail
            ));

        } catch (Exception e) {
            log.error("게임 AI 분석 테스트 실패: gameId={}, gameSeq={}", gameId, gameSeq, e);
            return ResponseEntity.ok(Map.of(
                "status", "error",
                "message", "AI 분석 실패: " + e.getMessage()
            ));
        }
    }

    /**
     * 데이터베이스 연결 테스트
     */
    @GetMapping("/db/games")
    public ResponseEntity<Object> testDatabaseConnection() {
        try {
            long totalGames = gameDetailRepository.count();
            
            // ai_status_code 기준으로 개수 조회
            long pendingGames = gameDetailRepository.countByAiStatusCode("B20005");
            long processingGames = gameDetailRepository.countByAiStatusCode("B20006");
            long completedGames = gameDetailRepository.countByAiStatusCode("B20007");
            long failedGames = gameDetailRepository.countByAiStatusCode("B20008");
            
            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "데이터베이스 연결 성공",
                "totalGameDetails", totalGames,
                "aiStatusBreakdown", Map.of(
                    "pending", pendingGames,
                    "processing", processingGames,
                    "completed", completedGames,
                    "failed", failedGames
                )
            ));
            
        } catch (Exception e) {
            log.error("데이터베이스 연결 테스트 실패", e);
            return ResponseEntity.ok(Map.of(
                "status", "error",
                "message", "데이터베이스 연결 실패: " + e.getMessage()
            ));
        }
    }

    /**
     * FastAPI DB 연결 테스트
     */
    @GetMapping("/fastapi/db-check")
    public ResponseEntity<Object> testFastAPIDatabase() {
        try {
            String result = aiClientService.testDatabaseConnection();
            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "FastAPI DB 연결 테스트 완료",
                "fastapi_result", result
            ));
        } catch (Exception e) {
            log.error("FastAPI DB 연결 테스트 실패", e);
            return ResponseEntity.ok(Map.of(
                "status", "error",
                "message", "FastAPI DB 연결 테스트 실패: " + e.getMessage()
            ));
        }
    }

    /**
     * FastAPI 단일 게임 처리 테스트
     */
    @PostMapping("/fastapi/process-one")
    public ResponseEntity<Object> testFastAPIProcessOne() {
        try {
            String result = aiClientService.testProcessOneGame();
            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "FastAPI 단일 게임 처리 테스트 완료",
                "fastapi_result", result
            ));
        } catch (Exception e) {
            log.error("FastAPI 단일 게임 처리 테스트 실패", e);
            return ResponseEntity.ok(Map.of(
                "status", "error",
                "message", "FastAPI 단일 게임 처리 테스트 실패: " + e.getMessage()
            ));
        }
    }

    /**
     * AI 분석 통계 조회 테스트
     */
    @GetMapping("/ai/statistics")
    public ResponseEntity<Object> testAIStatistics() {
        try {
            String result = aiClientService.getAnalysisStatistics();
            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "AI 분석 통계 조회 완료",
                "statistics", result
            ));
        } catch (Exception e) {
            log.error("AI 분석 통계 조회 테스트 실패", e);
            return ResponseEntity.ok(Map.of(
                "status", "error",
                "message", "AI 분석 통계 조회 실패: " + e.getMessage()
            ));
        }
    }

    /**
     * 실패한 게임 재처리 테스트
     */
    @PostMapping("/ai/reprocess")
    public ResponseEntity<Object> testReprocessFailedGames(@RequestParam(defaultValue = "5") int limit) {
        try {
            String result = aiClientService.requestReprocessFailedGames(limit);
            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "실패 게임 재처리 요청 완료",
                "limit", limit,
                "result", result
            ));
        } catch (Exception e) {
            log.error("실패 게임 재처리 테스트 실패", e);
            return ResponseEntity.ok(Map.of(
                "status", "error",
                "message", "실패 게임 재처리 테스트 실패: " + e.getMessage()
            ));
        }
    }

    // 헬퍼 메서드: 난이도 코드를 문자열로 변환
    private String mapDifficultyCodeToLevel(String difficultyCode) {
        switch (difficultyCode) {
            case "B20001": return "EASY";    // 초급
            case "B20002": return "NORMAL";  // 중급
            case "B20003": return "HARD";    // 고급
            case "B20004": return "EXPERT";  // 전문가
            default: return "NORMAL";
        }
    }
}