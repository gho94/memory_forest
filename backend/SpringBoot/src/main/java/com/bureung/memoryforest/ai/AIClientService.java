package com.bureung.memoryforest.ai;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.game.repository.GameMasterRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class AIClientService {

    @Value("${ai.service.url:http://ai-service:8000}")
    private String aiServiceUrl;

    private final RestTemplate restTemplate;
    private final GameMasterRepository gameMasterRepository;
    /**
     * 난이도별 AI 분석 (새로운 메서드)
     * FastAPI는 내부적으로 ai_status를 ai_status_code로 변환하여 저장
     */
    public AIAnalysisResponse analyzeAnswerWithDifficulty(String gameId, int gameSeq, String answerText, String difficultyLevel) {
        try {
            String url = aiServiceUrl + "/analyze";
            
            AIAnalysisRequest request = new AIAnalysisRequest();
            request.setGameId(gameId);
            request.setGameSeq(gameSeq);
            request.setAnswerText(answerText);
            request.setDifficultyLevel(difficultyLevel != null ? difficultyLevel : "NORMAL");

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<AIAnalysisRequest> entity = new HttpEntity<>(request, headers);

            log.info("난이도별 AI 분석 요청: gameId={}, answerText={}, difficulty={}", 
                    gameId, answerText, difficultyLevel);
            
            ResponseEntity<AIAnalysisResponse> response = restTemplate.postForEntity(
                url, entity, AIAnalysisResponse.class);

            AIAnalysisResponse aiResponse = response.getBody();
            
            if (aiResponse != null) {
                log.info("난이도별 AI 분석 완료: gameId={}, aiStatus={}, difficulty={}", 
                        gameId, aiResponse.getAiStatus(), difficultyLevel);
            }
            
            return aiResponse;
            
        } catch (Exception e) {
            log.error("난이도별 AI 분석 중 오류 발생: gameId={}, difficulty={}, error={}", 
                     gameId, difficultyLevel, e.getMessage());
            
            // 실패 응답 생성 - FastAPI와 동일한 형태
            AIAnalysisResponse failedResponse = new AIAnalysisResponse();
            failedResponse.setGameId(gameId);
            failedResponse.setGameSeq(gameSeq);
            failedResponse.setAiStatus("FAILED");  // FastAPI에서 B20008로 변환됨
            failedResponse.setDescription("AI 서비스 연결 실패 (난이도: " + difficultyLevel + "): " + e.getMessage());
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
     * 기존 메서드 (호환성 유지)
     */
    public AIAnalysisResponse analyzeAnswer(String gameId, int gameSeq, String answerText) {
        // ✅ 게임마스터 테이블에서 난이도 조회
        String difficultyLevel = getDifficultyFromGameMaster(gameId);
        return analyzeAnswerWithDifficulty(gameId, gameSeq, answerText, difficultyLevel);
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

    /**
     * 실패한 게임들 재처리 요청
     */
    public String requestReprocessFailedGames(int limit) {
        try {
            String url = aiServiceUrl + "/reprocess/failed?limit=" + limit;
            ResponseEntity<String> response = restTemplate.postForEntity(url, null, String.class);
            
            log.info("실패 게임 재처리 요청 완료: limit={}", limit);
            return response.getBody();
            
        } catch (Exception e) {
            log.error("실패 게임 재처리 요청 실패: error={}", e.getMessage());
            return "{\"error\":\"재처리 요청 실패: " + e.getMessage() + "\"}";
        }
    }

    /**
     * AI 분석 통계 조회
     */
    public String getAnalysisStatistics() {
        try {
            String url = aiServiceUrl + "/analysis/stats";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getBody();
        } catch (Exception e) {
            log.warn("AI 분석 통계 조회 실패: {}", e.getMessage());
            return "{\"error\":\"통계 조회 실패\"}";
        }
    }

    /**
     * 단일 게임 분석 테스트
     */
    public String testProcessOneGame() {
        try {
            String url = aiServiceUrl + "/test/process-one-game";
            ResponseEntity<String> response = restTemplate.postForEntity(url, null, String.class);
            
            log.info("단일 게임 분석 테스트 완료");
            return response.getBody();
            
        } catch (Exception e) {
            log.error("단일 게임 분석 테스트 실패: error={}", e.getMessage());
            return "{\"error\":\"테스트 실패: " + e.getMessage() + "\"}";
        }
    }

    /**
     * 데이터베이스 연결 테스트
     */
    public String testDatabaseConnection() {
        try {
            String url = aiServiceUrl + "/test/db-check";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getBody();
        } catch (Exception e) {
            log.warn("AI 서비스 DB 테스트 실패: {}", e.getMessage());
            return "{\"error\":\"DB 테스트 실패\"}";
        }
    }

    /**
     * 일반 배치 처리 요청
     */
    public String requestBatchProcessing(int limit) {
        try {
            String url = aiServiceUrl + "/batch/process?limit=" + limit;
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, null, String.class);
            
            log.info("배치 처리 요청 완료: limit={}", limit);
            return response.getBody();
            
        } catch (Exception e) {
            log.error("배치 처리 요청 실패: error={}", e.getMessage());
            return "{\"error\":\"배치 처리 요청 실패: " + e.getMessage() + "\"}";
        }
    }

    /**
     * 샘플 게임 조회
     */
    public String getSampleGames(int limit) {
        try {
            String url = aiServiceUrl + "/test/sample-games?limit=" + limit;
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getBody();
        } catch (Exception e) {
            log.warn("샘플 게임 조회 실패: {}", e.getMessage());
            return "{\"error\":\"샘플 게임 조회 실패\"}";
        }
    }

    /**
     * AI 서비스 전체 상태 체크
     */
    public String getServiceStatus() {
        try {
            String url = aiServiceUrl + "/";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getBody();
        } catch (Exception e) {
            log.warn("AI 서비스 상태 체크 실패: {}", e.getMessage());
            return "{\"error\":\"서비스 상태 체크 실패\"}";
        }
    }

    /**
     * 모델 정보 조회
     */
    public String getModelInfo() {
        try {
            String url = aiServiceUrl + "/model/info";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getBody();
        } catch (Exception e) {
            log.warn("모델 정보 조회 실패: {}", e.getMessage());
            return "{\"error\":\"모델 정보 조회 실패\"}";
        }
    }

    /**
     * 모델 리로드
     */
    public String reloadModel() {
        try {
            String url = aiServiceUrl + "/reload-model";
            ResponseEntity<String> response = restTemplate.postForEntity(url, null, String.class);
            
            log.info("모델 리로드 완료");
            return response.getBody();
            
        } catch (Exception e) {
            log.error("모델 리로드 실패: error={}", e.getMessage());
            return "{\"error\":\"모델 리로드 실패: " + e.getMessage() + "\"}";
        }
    }

    private String getDifficultyFromGameMaster(String gameId) {
        try {
            GameMaster gameMaster = gameMasterRepository.findById(gameId).orElse(null);
            
            if (gameMaster == null) {
                log.warn("게임마스터를 찾을 수 없음: gameId={}, 기본값(NORMAL) 사용", gameId);
                return "NORMAL";
            }
            
            String difficultyCode = gameMaster.getDifficultyLevelCode();
            if (difficultyCode == null || difficultyCode.trim().isEmpty()) {
                log.warn("난이도 코드가 null: gameId={}, 기본값(NORMAL) 사용", gameId);
                return "NORMAL";
            }
            
            String difficultyLevel = mapDifficultyCodeToLevel(difficultyCode);
            log.info("게임마스터에서 난이도 조회 성공: gameId={}, code={}, level={}", 
                    gameId, difficultyCode, difficultyLevel);
            
            return difficultyLevel;
            
        } catch (Exception e) {
            log.error("게임마스터 난이도 조회 실패: gameId={}, 기본값(NORMAL) 사용, error={}", 
                     gameId, e.getMessage());
            return "NORMAL";
        }
    }


    private String mapDifficultyCodeToLevel(String difficultyCode) {
        switch (difficultyCode) {
            case "B20001": return "EASY";    // 초급
            case "B20002": return "NORMAL";  // 중급
            case "B20003": return "HARD";    // 고급
            case "B20004": return "EXPERT";  // 전문가
            default: 
                log.warn("알 수 없는 난이도 코드: {}, 기본값(NORMAL) 사용", difficultyCode);
                return "NORMAL";
        }
    }

}