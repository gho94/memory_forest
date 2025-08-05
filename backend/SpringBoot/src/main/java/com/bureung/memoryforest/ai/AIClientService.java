package com.bureung.memoryforest.ai;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class AIClientService {

    @Value("${ai.service.url:http://ai-service:8000}")
    private String aiServiceUrl;

    private final RestTemplate restTemplate;

    /**
     * 난이도별 AI 분석 (새로운 메서드)
     */
    public AIAnalysisResponse analyzeAnswerWithDifficulty(String gameId, int gameSeq, String answerText, String difficultyLevel) {
        try {
            String url = aiServiceUrl + "/analyze";
            
            AIAnalysisRequest request = new AIAnalysisRequest();
            request.setAnswerText(answerText);
            request.setGameId(gameId);
            request.setGameSeq(gameSeq);
            request.setDifficultyLevel(difficultyLevel != null ? difficultyLevel : "NORMAL");

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<AIAnalysisRequest> entity = new HttpEntity<>(request, headers);

            log.info("난이도별 AI 분석 요청: gameId={}, answerText={}, difficulty={}", 
                    gameId, answerText, difficultyLevel);
            
            ResponseEntity<AIAnalysisResponse> response = restTemplate.postForEntity(
                url, entity, AIAnalysisResponse.class);

            log.info("난이도별 AI 분석 완료: gameId={}, status={}, difficulty={}", 
                    gameId, response.getBody().getAiStatus(), difficultyLevel);
            
            return response.getBody();
            
        } catch (Exception e) {
            log.error("난이도별 AI 분석 중 오류 발생: gameId={}, difficulty={}, error={}", 
                     gameId, difficultyLevel, e.getMessage());
            
            AIAnalysisResponse failedResponse = new AIAnalysisResponse();
            failedResponse.setGameId(gameId);
            failedResponse.setGameSeq(gameSeq);
            failedResponse.setAiStatus("FAILED");
            failedResponse.setDescription("AI 서비스 연결 실패 (난이도: " + difficultyLevel + "): " + e.getMessage());
            
            return failedResponse;
        }
    }

    /**
     * 기존 메서드 (호환성 유지)
     */
    public AIAnalysisResponse analyzeAnswer(String gameId, int gameSeq, String answerText) {
        return analyzeAnswerWithDifficulty(gameId, gameSeq, answerText, "NORMAL");
    }

    /**
     * 오버로딩 추가 (기존 호환성)
     */
    public AIAnalysisResponse analyzeAnswer(AIAnalysisRequest request) {
        return analyzeAnswerWithDifficulty(
            request.getGameId(), 
            request.getGameSeq(), 
            request.getAnswerText(),
            request.getDifficultyLevel()
        );
    }

    /**
     * 배치 분석 요청 (난이도별)
     */
    public String requestBatchAnalysisByDifficulty(String difficulty, int limit) {
        try {
            String url = aiServiceUrl + "/batch/process-by-difficulty?difficulty=" + difficulty + "&limit=" + limit;
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, null, String.class);
            
            log.info("난이도별 배치 분석 요청 완료: difficulty={}, limit={}", difficulty, limit);
            return response.getBody();
            
        } catch (Exception e) {
            log.error("난이도별 배치 분석 요청 실패: difficulty={}, error={}", difficulty, e.getMessage());
            return "{\"error\":\"배치 분석 요청 실패: " + e.getMessage() + "\"}";
        }
    }

    /**
     * AI 서비스 모델 상태 조회
     */
    public String getModelsStatus() {
        try {
            String url = aiServiceUrl + "/models/status";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getBody();
        } catch (Exception e) {
            log.warn("AI 서비스 모델 상태 조회 실패: {}", e.getMessage());
            return "{\"error\":\"모델 상태 조회 실패\"}";
        }
    }

    /**
     * 특정 난이도 모델 리로드
     */
    public String reloadDifficultyModel(String difficulty) {
        try {
            String url = aiServiceUrl + "/models/reload/" + difficulty;
            ResponseEntity<String> response = restTemplate.postForEntity(url, null, String.class);
            
            log.info("난이도 모델 리로드 완료: {}", difficulty);
            return response.getBody();
            
        } catch (Exception e) {
            log.error("난이도 모델 리로드 실패: difficulty={}, error={}", difficulty, e.getMessage());
            return "{\"error\":\"모델 리로드 실패: " + e.getMessage() + "\"}";
        }
    }

    public boolean isHealthy() {
        try {
            String url = aiServiceUrl + "/health";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            log.warn("AI 서비스 헬스체크 실패: {}", e.getMessage());
            return false;
        }
    }
}