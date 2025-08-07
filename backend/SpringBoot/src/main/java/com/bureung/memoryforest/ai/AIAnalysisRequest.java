package com.bureung.memoryforest.ai;

import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.ToString;

/**
 * AI 분석 요청 DTO (난이도 지원)
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
    private String difficultyLevel; // 난이도 필드 추가
}