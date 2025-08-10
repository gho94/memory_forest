package com.bureung.memoryforest.game.dto.request;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class CreateGamePlayerAnswerRequestDto {
    private String isCorrect;
    private int selectedOption;
    private int answerTimeMs;
    private String gameId;
    private int gameSeq;
}
