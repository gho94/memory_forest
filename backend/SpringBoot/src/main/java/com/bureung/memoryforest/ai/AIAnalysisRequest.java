package com.bureung.memoryforest.ai;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import com.fasterxml.jackson.annotation.JsonProperty;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AIAnalysisRequest {
    
    @JsonProperty("gameId")  // FastAPI의 snake_case에 맞춰 JSON 매핑
    private String gameId;
    
    @JsonProperty("gameSeq")
    private Integer gameSeq;
    
    @JsonProperty("answerText") 
    private String answerText;
    
    @JsonProperty("difficultyLevel")
    private String difficultyLevel;
}