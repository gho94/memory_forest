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

    // 기존 메서드
    public AIAnalysisResponse analyzeAnswer(String gameId, int gameSeq, String answerText) {
        try {
            String url = aiServiceUrl + "/analyze";
            
            AIAnalysisRequest request = new AIAnalysisRequest();
            request.setAnswerText(answerText);
            request.setGameId(gameId);
            request.setGameSeq(gameSeq);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<AIAnalysisRequest> entity = new HttpEntity<>(request, headers);

            log.info("AI 분석 요청: gameId={}, answerText={}", gameId, answerText);
            
            ResponseEntity<AIAnalysisResponse> response = restTemplate.postForEntity(
                url, entity, AIAnalysisResponse.class);

            log.info("AI 분석 완료: gameId={}, status={}", gameId, response.getBody().getAiStatus());
            
            return response.getBody();
            
        } catch (Exception e) {
            log.error("AI 분석 중 오류 발생: gameId={}, error={}", gameId, e.getMessage());
            
            AIAnalysisResponse failedResponse = new AIAnalysisResponse();
            failedResponse.setGameId(gameId);
            failedResponse.setGameSeq(gameSeq);
            failedResponse.setAiStatus("FAILED");
            failedResponse.setDescription("AI 서비스 연결 실패: " + e.getMessage());
            
            return failedResponse;
        }
    }

    // 오버로딩 추가 (GameMasterServiceImpl에 맞춤)
    public AIAnalysisResponse analyzeAnswer(AIAnalysisRequest request) {
        return analyzeAnswer(request.getGameId(), request.getGameSeq(), request.getAnswerText());
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
