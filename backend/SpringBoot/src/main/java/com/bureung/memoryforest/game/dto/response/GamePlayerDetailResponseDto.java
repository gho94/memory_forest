package com.bureung.memoryforest.game.dto.response;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class GamePlayerDetailResponseDto {
    private String gameId;
    private Integer gameSeq;
    private Integer selectedOption;
    private String isCorrect;
    private String gameTitle;
    private Integer scoreEarned;
    private String answerText;
    private String wrongOption1;
    private String wrongOption2;
    private String wrongOption3;
    private Integer fileId;
    private String status;
}