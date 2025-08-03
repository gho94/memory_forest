package com.bureung.memoryforest.game.dto.response;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class GameDetailResponseDto {
    private String gameId;
    private Integer gameSeq;
    private Integer gameOrder;
    private String categoryCode;
    private String originalName;
    private String fileName;
    private String filePath;
    private Long fileSize;
    private String mimeType;
    private String answerText;
    private String wrongOption1;
    private String wrongOption2;
    private String wrongOption3;
    private String aiStatus;
    private String description;
    private Double similarityScore1;
    private Double similarityScore2;
    private Double similarityScore3;
}
