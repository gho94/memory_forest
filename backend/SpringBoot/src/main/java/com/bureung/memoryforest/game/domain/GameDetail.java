package com.bureung.memoryforest.game.domain;

import lombok.*;
import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 게임 세부 정보를 저장하는 엔티티
 * 각 게임의 개별 문제/이미지 데이터를 관리
 */
@Entity
@Table(name = "game_detail")
@IdClass(GameDetailId.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GameDetail {
    @Id
    @Column(name = "game_id", nullable = false, length = 10)
    private String gameId;

    @Id
    @Column(name = "game_seq", nullable = false)
    private Integer gameSeq;

    @Column(name = "game_order", nullable = false)
    private Integer gameOrder;

    @Column(name = "file_id", nullable = false)
    private Integer fileId;

    @Column(name = "answer_text", nullable = true, length = 20)
    private String answerText;

    @Column(name = "wrong_option_1", nullable = true, length = 20)
    private String wrongOption1;

    @Column(name = "wrong_option_2", nullable = true, length = 20)
    private String wrongOption2;

    @Column(name = "wrong_option_3", nullable = true, length = 20)
    private String wrongOption3;

    @Column(name = "wrong_score_1", nullable = true)
    private Integer wrongScore1;

    @Column(name = "wrong_score_2", nullable = true)
    private Integer wrongScore2;

    @Column(name = "wrong_score_3", nullable = true)
    private Integer wrongScore3;

    @Column(name = "ai_status_code", nullable = false, length = 6)
    private String aiStatusCode;

    @Column(name = "ai_processed_at", nullable = true)  
    private LocalDateTime aiProcessedAt;

    @Column(name = "description", nullable = true, length = 200)
    private String description;

    /**
     * AI 분석 결과를 업데이트하는 메서드
     */
    public void updateAIAnalysisResult(String wrongOption1, String wrongOption2, String wrongOption3,
                                     Double wrongScore1, Double wrongScore2, Double wrongScore3,
                                     String aiStatus, String description) {
        this.wrongOption1 = wrongOption1;
        this.wrongOption2 = wrongOption2;
        this.wrongOption3 = wrongOption3;
        this.wrongScore1 = wrongScore1.intValue();
        this.wrongScore2 = wrongScore2.intValue();
        this.wrongScore3 = wrongScore3.intValue();
        this.aiStatusCode = aiStatus;
        this.description = description;
        this.aiProcessedAt = LocalDateTime.now();
    }

    /**
     * AI 분석 실패 처리
     */
    public void markAIAnalysisFailed(String errorMessage) {
        this.aiStatusCode = "FAILED";
        this.description = errorMessage;
        this.aiProcessedAt = LocalDateTime.now();
    }

    /**
     * AI 분석 진행 중 상태로 변경
     */
    public void markAIAnalyzing() {
        this.aiStatusCode = "ANALYZING";
        this.description = "AI 분석 진행중";
        this.aiProcessedAt = LocalDateTime.now();
    }

    /**
     * AI 분석이 필요한지 확인
     */
    public boolean needsAIAnalysis() {
        return this.answerText != null && 
               !this.answerText.trim().isEmpty() && 
               ("PENDING".equals(this.aiStatusCode) || "FAILED".equals(this.aiStatusCode));
    }

    /**
     * AI 분석이 완료되었는지 확인
     */
    public boolean isAIAnalysisCompleted() {
        return "COMPLETED".equals(this.aiStatusCode) && 
               this.wrongOption1 != null && 
               this.wrongOption2 != null && 
               this.wrongOption3 != null;
    }
}