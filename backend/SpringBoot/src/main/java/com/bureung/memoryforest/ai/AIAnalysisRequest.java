package com.bureung.memoryforest.ai;


// AIAnalysisRequest.java - 타입 확인 및 수정

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.ToString;

@Data
@ToString
public class AIAnalysisRequest {
    
    @JsonProperty("gameId")
    private String gameId;
    
    @JsonProperty("gameSeq")
    private Integer gameSeq;
    
    @JsonProperty("answerText")
    private String answerText;
    
    @JsonProperty("difficultyLevel")
    private String difficultyLevel;
    
    // 기본 생성자
    public AIAnalysisRequest() {}
    
    // 전체 생성자
    public AIAnalysisRequest(String gameId, Integer gameSeq, String answerText, String difficultyLevel) {
        this.gameId = gameId;
        this.gameSeq = gameSeq;
        this.answerText = answerText;
        this.difficultyLevel = difficultyLevel != null ? difficultyLevel : "NORMAL";
    }
}