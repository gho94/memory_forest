package com.bureung.memoryforest.ai;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class AIClientService {

    @Value("${ai.service.url:http://ai-service:8000}")
    private String aiServiceUrl;

    private final RestTemplate restTemplate;

    public String getAiServiceUrl() {
    return aiServiceUrl;
    }
    
    /**
     * 난이도별 AI 분석 (JSON 매핑 개선)
     */
    public AIAnalysisResponse analyzeAnswerWithDifficulty(String gameId, int gameSeq, String answerText, String difficultyLevel) {
        try {
            String url = aiServiceUrl + "/analyze";
            
            // 요청 객체 생성 및 로깅
            AIAnalysisRequest request = new AIAnalysisRequest();
            request.setGameId(gameId);
            request.setGameSeq(gameSeq);
            request.setAnswerText(answerText);
            request.setDifficultyLevel(difficultyLevel != null ? difficultyLevel : "NORMAL");

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<AIAnalysisRequest> entity = new HttpEntity<>(request, headers);

            log.info("=== AI 서비스 요청 시작 ===");
            log.info("URL: {}", url);
            log.info("요청 헤더: {}", headers);
            log.info("요청 객체: gameId={}, gameSeq={}, answerText='{}', difficultyLevel={}", 
                    request.getGameId(), request.getGameSeq(), request.getAnswerText(), request.getDifficultyLevel());
            
            // 요청 JSON 로깅 (디버그용)
            try {
                ObjectMapper objectMapper = new ObjectMapper();
                String requestJson = objectMapper.writeValueAsString(request);
                log.info("요청 JSON: {}", requestJson);
            } catch (Exception e) {
                log.warn("요청 JSON 직렬화 실패: {}", e.getMessage());
            }
            
            // AI 서비스 응답 시간 측정
            long startTime = System.currentTimeMillis();
            
            ResponseEntity<String> rawResponse = restTemplate.postForEntity(url, entity, String.class);
            
            long endTime = System.currentTimeMillis();
            log.info("AI 서비스 응답 시간: {}ms", endTime - startTime);
            log.info("원본 응답 상태: {}", rawResponse.getStatusCode());
            log.info("원본 응답 JSON: {}", rawResponse.getBody());

            // JSON을 수동으로 파싱하여 응답 객체 생성
            AIAnalysisResponse response = parseAIResponse(rawResponse.getBody(), gameId, gameSeq);
            
            log.info("=== 파싱된 AI 분석 응답 ===");
            log.info("gameId: {}", response.getGameId());
            log.info("gameSeq: {}", response.getGameSeq());
            log.info("aiStatus: {}", response.getAiStatus());
            log.info("description: {}", response.getDescription());
            log.info("wrongOption1: '{}'", response.getWrongOption1());
            log.info("wrongOption2: '{}'", response.getWrongOption2());
            log.info("wrongOption3: '{}'", response.getWrongOption3());
            log.info("wrongScore1: {}", response.getWrongScore1());
            log.info("wrongScore2: {}", response.getWrongScore2());
            log.info("wrongScore3: {}", response.getWrongScore3());
            log.info("=== AI 분석 응답 완료 ===");
            
            return response;
            
        } catch (Exception e) {
            log.error("=== AI 분석 중 오류 발생 ===");
            log.error("gameId: {}, difficulty: {}", gameId, difficultyLevel);
            log.error("오류 타입: {}", e.getClass().getSimpleName());
            log.error("오류 메시지: {}", e.getMessage());
            log.error("전체 스택 트레이스:", e);
            
            AIAnalysisResponse failedResponse = new AIAnalysisResponse();
            failedResponse.setGameId(gameId);
            failedResponse.setGameSeq(gameSeq);
            failedResponse.setAiStatus("FAILED");
            failedResponse.setDescription("AI 서비스 연결 실패: " + e.getMessage());
            // 기본값 설정
            failedResponse.setWrongOption1("");
            failedResponse.setWrongOption2("");
            failedResponse.setWrongOption3("");
            failedResponse.setWrongScore1(0.0);
            failedResponse.setWrongScore2(0.0);
            failedResponse.setWrongScore3(0.0);
            
            return failedResponse;
        }
    }

    /**
     * AI 응답 JSON을 수동으로 파싱 (매핑 문제 해결)
     */
    private AIAnalysisResponse parseAIResponse(String jsonResponse, String gameId, int gameSeq) {
        AIAnalysisResponse response = new AIAnalysisResponse();
        
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode jsonNode = objectMapper.readTree(jsonResponse);
            
            // 필드별로 안전하게 파싱
            response.setGameId(getStringValue(jsonNode, "gameId", gameId));
            response.setGameSeq(getIntValue(jsonNode, "gameSeq", gameSeq));
            response.setAiStatus(getStringValue(jsonNode, "aiStatus", "FAILED"));
            response.setDescription(getStringValue(jsonNode, "description", ""));
            
            response.setWrongOption1(getStringValue(jsonNode, "wrongOption1", ""));
            response.setWrongOption2(getStringValue(jsonNode, "wrongOption2", ""));
            response.setWrongOption3(getStringValue(jsonNode, "wrongOption3", ""));
            
            response.setWrongScore1(getDoubleValue(jsonNode, "wrongScore1", 0.0));
            response.setWrongScore2(getDoubleValue(jsonNode, "wrongScore2", 0.0));
            response.setWrongScore3(getDoubleValue(jsonNode, "wrongScore3", 0.0));
            
            log.info("JSON 파싱 성공: aiStatus={}, wrongOption1='{}'", 
                    response.getAiStatus(), response.getWrongOption1());
            
        } catch (Exception e) {
            log.error("JSON 파싱 실패: {}", e.getMessage(), e);
            // 실패 시 기본값으로 설정
            response.setGameId(gameId);
            response.setGameSeq(gameSeq);
            response.setAiStatus("FAILED");
            response.setDescription("JSON 파싱 실패: " + e.getMessage());
            response.setWrongOption1("");
            response.setWrongOption2("");
            response.setWrongOption3("");
            response.setWrongScore1(0.0);
            response.setWrongScore2(0.0);
            response.setWrongScore3(0.0);
        }
        
        return response;
    }
    
    private String getStringValue(JsonNode node, String fieldName, String defaultValue) {
        JsonNode field = node.get(fieldName);
        return field != null && !field.isNull() ? field.asText() : defaultValue;
    }
    
    private int getIntValue(JsonNode node, String fieldName, int defaultValue) {
        JsonNode field = node.get(fieldName);
        return field != null && !field.isNull() ? field.asInt() : defaultValue;
    }
    
    private Double getDoubleValue(JsonNode node, String fieldName, double defaultValue) {
        JsonNode field = node.get(fieldName);
        return field != null && !field.isNull() ? field.asDouble() : defaultValue;
    }

    /**
     * AI 서비스 연결 테스트
     */
    public boolean testConnection() {
        try {
            String url = aiServiceUrl + "/health";
            log.info("=== AI 서비스 연결 테스트 시작 ===");
            log.info("테스트 URL: {}", url);
            
            long startTime = System.currentTimeMillis();
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            long endTime = System.currentTimeMillis();
            
            log.info("연결 테스트 결과:");
            log.info("- 응답 시간: {}ms", endTime - startTime);
            log.info("- 상태 코드: {}", response.getStatusCode());
            log.info("- 응답 본문: {}", response.getBody());
            log.info("=== AI 서비스 연결 테스트 완료 ===");
            
            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            log.error("=== AI 서비스 연결 테스트 실패 ===");
            log.error("URL: {}", aiServiceUrl + "/health");
            log.error("오류: {}", e.getMessage(), e);
            return false;
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
        // 요청 전 연결 테스트
        if (!testConnection()) {
            log.error("AI 서비스에 연결할 수 없습니다. URL: {}", aiServiceUrl);
            AIAnalysisResponse failedResponse = new AIAnalysisResponse();
            failedResponse.setGameId(request.getGameId());
            failedResponse.setGameSeq(request.getGameSeq());
            failedResponse.setAiStatus("FAILED");
            failedResponse.setDescription("AI 서비스 연결 불가: " + aiServiceUrl);
            return failedResponse;
        }

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

    /**
     * AI 서비스 헬스체크
     */
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