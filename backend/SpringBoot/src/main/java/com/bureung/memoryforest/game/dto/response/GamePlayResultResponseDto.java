package com.bureung.memoryforest.game.dto.response;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
public class GamePlayResultResponseDto {
    private String gameId;
    private String playerId;
    private Integer totalScore;
    private Integer correctCount;
    private BigDecimal accuracyRate;  // 0.0 ~ 100.0
    private Integer durationSeconds;

    public GamePlayResultResponseDto(String gameId, String playerId,
                                     Long totalScore, Long correctCount,
                                     BigDecimal accuracyRate, Long durationSeconds) {
        this.gameId = gameId;
        this.playerId = playerId;
        this.totalScore = totalScore != null ? totalScore.intValue() : 0;
        this.correctCount = correctCount != null ? correctCount.intValue() : 0;
        this.accuracyRate = accuracyRate != null ? accuracyRate : BigDecimal.ZERO;
        this.durationSeconds = durationSeconds != null ? durationSeconds.intValue() : 0;
    }
}
