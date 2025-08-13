package com.bureung.memoryforest.game.domain;

import lombok.*;
import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 게임 세부 정보를 저장하는 엔티티
 * 각 게임의 개별 문제/이미지 데이터를 관리
 * init.sql의 ai_status_code 컬럼에 맞춰 수정
 */
@Entity
@Table(name = "game_detail")
@IdClass(GameDetailId.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@ToString
public class GameDetail {

    @Id
    @Column(name = "game_id", length = 10, nullable = false)
    private String gameId;

    @Id
    @Column(name = "game_seq", nullable = false)
    private Integer gameSeq;

    @Column(name = "game_order", nullable = false)
    private Integer gameOrder;

    @Column(name = "game_title", length = 100, nullable = false)
    private String gameTitle;

    @Column(name = "game_desc", length = 200)
    private String gameDesc;

    @Column(name = "file_id", nullable = false)
    private Integer fileId;

    @Column(name = "answer_text", length = 20)
    private String answerText;

    @Column(name = "wrong_option_1", length = 20)
    private String wrongOption1;

    @Column(name = "wrong_option_2", length = 20)
    private String wrongOption2;

    @Column(name = "wrong_option_3", length = 20)
    private String wrongOption3;

    @Column(name = "wrong_score_1")
    private Double wrongScore1;

    @Column(name = "wrong_score_2")  
    private Double wrongScore2;

    @Column(name = "wrong_score_3")
    private Double wrongScore3;

    // AI 상태는 하나의 필드로 통일 (DB 스키마에 맞춤)
    @Column(name = "ai_status_code", nullable = false, length = 6)
    @Builder.Default
    private String aiStatusCode = "B20005";  // 대기중 상태 코드

    @Column(name = "ai_processed_at")
    private LocalDateTime aiProcessedAt;

    @Column(name = "description", length = 200)
    private String description;

    // ========== 필수 메서드들 ==========
    
    /**
     * AI 분석이 필요한지 확인
     */
    public boolean needsAIAnalysis() {
        return answerText != null && 
               !answerText.trim().isEmpty() && 
               ("B20005".equals(aiStatusCode) || "B20008".equals(aiStatusCode)); // 대기중 또는 실패
    }

    /**
     * AI 분석 결과 업데이트 (Integer 버전)
     */
    public void updateAIAnalysisResult(String wrongOption1, String wrongOption2, String wrongOption3,
                                     Integer wrongScore1, Integer wrongScore2, Integer wrongScore3,
                                     String aiStatusCode, String description) {
        this.wrongOption1 = wrongOption1;
        this.wrongOption2 = wrongOption2;
        this.wrongOption3 = wrongOption3;
        this.wrongScore1 = wrongScore1 != null ? wrongScore1.doubleValue() : null;
        this.wrongScore2 = wrongScore2 != null ? wrongScore2.doubleValue() : null;
        this.wrongScore3 = wrongScore3 != null ? wrongScore3.doubleValue() : null;
        this.aiStatusCode = aiStatusCode;
        this.description = description;
        this.aiProcessedAt = LocalDateTime.now();
    }

    /**
     * AI 분석 결과 업데이트 (Double 버전)
     */
    public void updateAIAnalysisResult(String wrongOption1, String wrongOption2, String wrongOption3,
                                     Double wrongScore1, Double wrongScore2, Double wrongScore3,
                                     String aiStatusCode, String description) {
        this.wrongOption1 = wrongOption1;
        this.wrongOption2 = wrongOption2;
        this.wrongOption3 = wrongOption3;
        this.wrongScore1 = wrongScore1;
        this.wrongScore2 = wrongScore2;
        this.wrongScore3 = wrongScore3;
        this.aiStatusCode = aiStatusCode;
        this.description = description;
        this.aiProcessedAt = LocalDateTime.now();
    }

    /**
     * AI 분석 시작 표시
     */
    public void markAIAnalyzing() {
        this.aiStatusCode = "B20006"; // 생성중 상태
        this.description = "AI 분석 중...";
    }

    /**
     * AI 분석 실패 표시
     */
    public void markAIAnalysisFailed(String errorMessage) {
        this.aiStatusCode = "B20008"; // 실패 상태
        this.description = errorMessage;
        this.aiProcessedAt = LocalDateTime.now();
    }

    /**
     * AI 분석 완료 여부 확인
     */
    public boolean isAIAnalysisCompleted() {
        return "B20007".equals(this.aiStatusCode); // 완료 상태
    }

    /**
     * AI 분석 대기 중인지 확인
     */
    public boolean isAIAnalysisPending() {
        return "B20005".equals(this.aiStatusCode); // 대기중 상태
    }

    // ========== FastAPI 연동을 위한 메서드들 ==========
    
    /**
     * FastAPI에 전달할 AI 상태 문자열 반환
     * FastAPI는 문자열 상태를 받아서 내부적으로 코드로 변환
     */
    public String getAiStatusForAPI() {
        return mapStatusCodeToString(this.aiStatusCode);
    }

    /**
     * FastAPI로부터 받은 문자열 상태를 코드로 설정
     */
    public void setAiStatusFromAPI(String aiStatus) {
        this.aiStatusCode = mapStringToStatusCode(aiStatus);
    }

    // 호환성을 위한 메서드들 (기존 코드가 aiStatus를 사용하는 경우)
    public String getAiStatus() {
        return mapStatusCodeToString(this.aiStatusCode);
    }

    public void setAiStatus(String aiStatus) {
        this.aiStatusCode = mapStringToStatusCode(aiStatus);
    }

    // ========== 상태 코드와 문자열 간 매핑 ==========
    
    /**
     * 상태 코드를 FastAPI용 문자열로 변환
     */
    private String mapStatusCodeToString(String statusCode) {
        if (statusCode == null) return "PENDING";
        
        switch (statusCode) {
            case "B20005": return "PENDING";
            case "B20006": return "PROCESSING";
            case "B20007": return "COMPLETED";
            case "B20008": return "FAILED";
            default: return "PENDING";
        }
    }

    /**
     * FastAPI용 문자열을 상태 코드로 변환
     */
    private String mapStringToStatusCode(String status) {
        if (status == null) return "B20005";
        
        switch (status.toUpperCase()) {
            case "PENDING": return "B20005";
            case "PROCESSING": return "B20006";
            case "COMPLETED": return "B20007";
            case "FAILED": return "B20008";
            default: return "B20005";
        }
    }

    // ========== 편의 메서드들 ==========
    
    /**
     * AI 분석 상태가 진행 중인지 확인
     */
    public boolean isAIAnalysisInProgress() {
        return "B20006".equals(this.aiStatusCode);
    }

    /**
     * AI 분석 상태가 실패인지 확인
     */
    public boolean isAIAnalysisFailed() {
        return "B20008".equals(this.aiStatusCode);
    }

    /**
     * 재분석이 필요한지 확인 (실패 또는 대기 상태)
     */
    public boolean needsReanalysis() {
        return "B20005".equals(this.aiStatusCode) || "B20008".equals(this.aiStatusCode);
    }
}