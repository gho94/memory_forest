package com.bureung.memoryforest.ai;

import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.ToString;

/**
 * AI 분석 응답 DTO
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@ToString
public class AIAnalysisResponse {
    private String gameId;
    private int gameSeq;
    private String wrongOption1;
    private String wrongOption2;
    private String wrongOption3;
    private Double similarityScore1;
    private Double similarityScore2;
    private Double similarityScore3;
    private String aiStatus;
    private String description;
}