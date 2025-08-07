package com.bureung.memoryforest.ai;
// AIAnalysisResponse.java - 타입 확인 및 수정

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.ToString;

@Data
@ToString
public class AIAnalysisResponse {
    
    @JsonProperty("gameId")
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
    private Double wrongScore1;  // Double 타입 확인
    
    @JsonProperty("wrongScore2") 
    private Double wrongScore2;  // Double 타입 확인
    
    @JsonProperty("wrongScore3")
    private Double wrongScore3;  // Double 타입 확인
    
    @JsonProperty("aiStatus")
    private String aiStatus;
    
    @JsonProperty("description")
    private String description;
    
    // 기본 생성자
    public AIAnalysisResponse() {}
    
    // 필요한 생성자
    public AIAnalysisResponse(String gameId, Integer gameSeq) {
        this.gameId = gameId;
        this.gameSeq = gameSeq;
        // 기본값 설정
        this.wrongOption1 = "";
        this.wrongOption2 = "";
        this.wrongOption3 = "";
        this.wrongScore1 = 0.0;
        this.wrongScore2 = 0.0;
        this.wrongScore3 = 0.0;
        this.aiStatus = "PENDING";
        this.description = "";
    }
}