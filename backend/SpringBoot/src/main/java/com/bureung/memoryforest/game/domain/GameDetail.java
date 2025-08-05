package com.bureung.memoryforest.game.domain;

import lombok.*;
import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 게임 세부 정보를 저장하는 엔티티
 * 각 게임의 개별 문제/이미지 데이터를 관리
 */
@Entity
@Table(name = "GAME_DETAIL")
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
    private String aiStatus = "PENDING";

    @Column(name = "AI_PROCESSED_AT")
    private LocalDateTime aiProcessedAt;

    @Column(name = "DESCRIPTION", length = 500)
    private String description;

    // DB 명세서에 따라 NUMBER 타입이므로 String이 아닌 Double로 수정
    @Column(name = "WRONG_SCORE_1")
    private Double wrongScore1;

    @Column(name = "WRONG_SCORE_2")  
    private Double wrongScore2;

    @Column(name = "WRONG_SCORE_3")
    private Double wrongScore3;

    /**
     * AI 분석 결과를 업데이트하는 메서드
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
     * AI 분석 실패 처리
     */
    public void markAIAnalysisFailed(String errorMessage) {
        this.aiStatus = "FAILED";
        this.description = errorMessage;
        this.aiProcessedAt = LocalDateTime.now();
    }

    /**
     * AI 분석 진행 중 상태로 변경
     */
    public void markAIAnalyzing() {
        this.aiStatus = "ANALYZING";
        this.description = "AI 분석 진행중";
        this.aiProcessedAt = LocalDateTime.now();
    }

    /**
     * AI 분석이 필요한지 확인
     */
    public boolean needsAIAnalysis() {
        return this.answerText != null && 
               !this.answerText.trim().isEmpty() && 
               ("PENDING".equals(this.aiStatus) || "FAILED".equals(this.aiStatus));
    }

    /**
     * AI 분석이 완료되었는지 확인
     */
    public boolean isAIAnalysisCompleted() {
        return "COMPLETED".equals(this.aiStatus) && 
               this.wrongOption1 != null && 
               this.wrongOption2 != null && 
               this.wrongOption3 != null;
    }
}