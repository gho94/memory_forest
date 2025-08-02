package com.bureung.memoryforest.ai;

import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.ToString;

/**
 * AI 분석 요청 DTO
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@ToString
public class AIAnalysisRequest {
    private String answerText;
    private String gameId;
    private int gameSeq;
}