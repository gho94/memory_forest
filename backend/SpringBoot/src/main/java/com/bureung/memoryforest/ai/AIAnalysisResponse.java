package com.bureung.memoryforest.ai;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import com.fasterxml.jackson.annotation.JsonProperty;

@Data
@NoArgsConstructor  
@AllArgsConstructor
public class AIAnalysisResponse {
    
    @JsonProperty("gameId")  // FastAPI의 camelCase response에 맞춰 JSON 매핑
    private String gameId;
    
    @JsonProperty("gameSeq")
    private Integer gameSeq;
    
    @JsonProperty("wrongOption1")
    private String wrongOption1;
    
    @JsonProperty("wrongOption2")
    private String wrongOption2;
    
    @JsonProperty("wrongOption3")
    private String wrongOption3;
    
    @JsonProperty("wrongScore1")
    private Double wrongScore1;
    
    @JsonProperty("wrongScore2")
    private Double wrongScore2;
    
    @JsonProperty("wrongScore3")
    private Double wrongScore3;
    
    @JsonProperty("aiStatus")
    private String aiStatus;
    
    @JsonProperty("description")
    private String description;
}