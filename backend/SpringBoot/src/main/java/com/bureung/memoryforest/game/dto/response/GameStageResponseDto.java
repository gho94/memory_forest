package com.bureung.memoryforest.game.dto.response;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class GameStageResponseDto {
    private String gameId;
    private Integer gameSeq;
    private String answerText;
    private String wrongOption1;
    private String wrongOption2;
    private String wrongOption3;
    private int currentProgress;
    private int totalQuestions;
}
