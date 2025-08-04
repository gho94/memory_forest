package com.bureung.memoryforest.game.dto.response;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class GamePlayResultResponseDto {
    private String gameId;
    private String playerId;
    private Integer totalScore;
    private Integer correctCount;
    private Double accuracyRate;  // 0.0 ~ 100.0
}
