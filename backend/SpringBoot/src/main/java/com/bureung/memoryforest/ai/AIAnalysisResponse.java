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
    private Double wrongScore1;
    private Double wrongScore2;
    private Double wrongScore3;
    private String aiStatus;
    private String description;
}
