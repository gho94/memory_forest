package com.bureung.memoryforest.test.controller;

import com.bureung.memoryforest.ai.AIAnalysisRequest;
import com.bureung.memoryforest.ai.AIAnalysisResponse;
import com.bureung.memoryforest.ai.AIClientService;
import com.bureung.memoryforest.game.domain.GameDetail;
import com.bureung.memoryforest.game.repository.GameDetailRepository;
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

    /**
     * FastAPI 연결 테스트
     */
    @GetMapping("/fastapi/health")
    public ResponseEntity<Map<String, String>> testFastAPIHealth() {
        try {
            // TODO: AIClientService에 health check 메서드 추가
            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "FastAPI 연결 테스트 준비됨"
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

            // AI 분석 요청
            AIAnalysisResponse response = aiClientService.analyzeAnswerWithDifficulty(
                gameId, gameSeq, gameDetail.getAnswerText(), "NORMAL");

            // 결과를 GameDetail에 저장
            if ("COMPLETED".equals(response.getAiStatus())) {
                gameDetail.updateAIAnalysisResult(
                    response.getWrongOption1(),
                    response.getWrongOption2(), 
                    response.getWrongOption3(),
                    response.getWrongScore1() != null ? response.getWrongScore1().intValue() : 0,
                    response.getWrongScore2() != null ? response.getWrongScore2().intValue() : 0,
                    response.getWrongScore3() != null ? response.getWrongScore3().intValue() : 0,
                    "B20005", // 완료 상태 코드
                    response.getDescription()
                );
                gameDetailRepository.save(gameDetail);
                
                log.info("AI 분석 결과 저장 완료: gameId={}, gameSeq={}", gameId, gameSeq);
            }

            return ResponseEntity.ok(Map.of(
                "status", "success",
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
            
            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "데이터베이스 연결 성공",
                "totalGameDetails", totalGames
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
     * 샘플 게임 데이터 생성 (테스트용)
     */
    @PostMapping("/create-sample-game")
    public ResponseEntity<Object> createSampleGame() {
        try {
            // TODO: 실제 파일 업로드 없이 테스트용 게임 데이터 생성
            // 이 부분은 실제 GameCommandService를 사용하거나
            // 직접 GameDetail을 생성할 수 있습니다.
            
            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "샘플 게임 생성 기능은 구현 예정입니다"
            ));
            
        } catch (Exception e) {
            log.error("샘플 게임 생성 실패", e);
            return ResponseEntity.ok(Map.of(
                "status", "error", 
                "message", "샘플 게임 생성 실패: " + e.getMessage()
            ));
        }
    }
}