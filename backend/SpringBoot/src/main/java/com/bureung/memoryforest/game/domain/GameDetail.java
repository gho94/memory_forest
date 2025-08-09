package com.bureung.memoryforest.game.domain;

import lombok.*;
import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 게임 세부 정보를 저장하는 엔티티
 * 각 게임의 개별 문제/이미지 데이터를 관리
 */
@Entity
@Table(name = "GAME_DETAIL")  // 기존 테이블명 유지
@IdClass(GameDetailId.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@ToString(exclude = {"filePath"})
public class GameDetail {

    @Id
    @Column(name = "GAME_ID", length = 10, nullable = false)
    private String gameId;

    @Id
    @Column(name = "GAME_SEQ", nullable = false)
    private Integer gameSeq;

    @Column(name = "GAME_ORDER", nullable = false)
    private Integer gameOrder;

    @Column(name = "CATEGORY_CODE", length = 6, nullable = false)
    private String categoryCode;

    @Column(name = "ORIGINAL_NAME", nullable = false, length = 255)
    private String originalName;

    @Column(name = "FILE_NAME", nullable = false, length = 255)
    private String fileName;

    @Column(name = "FILE_PATH", length = 500, nullable = false)
    private String filePath;

    @Column(name = "FILE_SIZE", nullable = false)
    private Long fileSize;

    @Column(name = "MIME_TYPE", length = 50, nullable = false)
    private String mimeType;

    @Column(name = "ANSWER_TEXT", length = 20)
    private String answerText;

    @Column(name = "WRONG_OPTION_1", length = 20)
    private String wrongOption1;

    @Column(name = "WRONG_OPTION_2", length = 20)
    private String wrongOption2;

    @Column(name = "WRONG_OPTION_3", length = 20)
    private String wrongOption3;

    @Column(name = "AI_STATUS", length = 10, nullable = false)
    @Builder.Default
    private String aiStatus = "PENDING";  // ✅ 기존 필드명 유지

    @Column(name = "AI_PROCESSED_AT")
    private LocalDateTime aiProcessedAt;

    @Column(name = "DESCRIPTION", length = 500)
    private String description;

    @Column(name = "WRONG_SCORE_1")
    private Double wrongScore1;

    @Column(name = "WRONG_SCORE_2")  
    private Double wrongScore2;

    @Column(name = "WRONG_SCORE_3")
    private Double wrongScore3;

    // ========== 필수 메서드들 추가 ==========
    
    /**
     * AI 분석이 필요한지 확인
     */
    public boolean needsAIAnalysis() {
        return answerText != null && 
               !answerText.trim().isEmpty() && 
               ("PENDING".equals(aiStatus) || "FAILED".equals(aiStatus));
    }

    /**
     * AI 분석 결과 업데이트 (Integer 버전 - 타입 변환 해결)
     */
    public void updateAIAnalysisResult(String wrongOption1, String wrongOption2, String wrongOption3,
                                     Integer wrongScore1, Integer wrongScore2, Integer wrongScore3,
                                     String aiStatus, String description) {
        this.wrongOption1 = wrongOption1;
        this.wrongOption2 = wrongOption2;
        this.wrongOption3 = wrongOption3;
        this.wrongScore1 = wrongScore1 != null ? wrongScore1.doubleValue() : null;
        this.wrongScore2 = wrongScore2 != null ? wrongScore2.doubleValue() : null;
        this.wrongScore3 = wrongScore3 != null ? wrongScore3.doubleValue() : null;
        this.aiStatus = aiStatus;
        this.description = description;
        this.aiProcessedAt = LocalDateTime.now();
    }

    /**
     * AI 분석 결과 업데이트 (Double 버전 - 기존 호환성)
     */
    public void updateAIAnalysisResult(String wrongOption1, String wrongOption2, String wrongOption3,
                                     Double wrongScore1, Double wrongScore2, Double wrongScore3,
                                     String aiStatus, String description) {
        this.wrongOption1 = wrongOption1;
        this.wrongOption2 = wrongOption2;
        this.wrongOption3 = wrongOption3;
        this.wrongScore1 = wrongScore1;
        this.wrongScore2 = wrongScore2;
        this.wrongScore3 = wrongScore3;
        this.aiStatus = aiStatus;
        this.description = description;
        this.aiProcessedAt = LocalDateTime.now();
    }

    /**
     * AI 분석 시작 표시
     */
    public void markAIAnalyzing() {
        this.aiStatus = "PROCESSING";
        this.description = "AI 분석 중...";
    }

    /**
     * AI 분석 실패 표시
     */
    public void markAIAnalysisFailed(String errorMessage) {
        this.aiStatus = "FAILED";
        this.description = errorMessage;
        this.aiProcessedAt = LocalDateTime.now();
    }

    /**
     * AI 분석 완료 여부 확인
     */
    public boolean isAIAnalysisCompleted() {
        return "COMPLETED".equals(this.aiStatus);
    }

    /**
     * AI 분석 대기 중인지 확인
     */
    public boolean isAIAnalysisPending() {
        return "PENDING".equals(this.aiStatus);
    }
}