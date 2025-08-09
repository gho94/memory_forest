package com.bureung.memoryforest.game.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;

@Getter
@Builder
@AllArgsConstructor
public class GameRecorderDashboardResponseDto {
    private String gameId;
    private int currentProgress;
    private int totalQuestions;
    private boolean isNewGame;
    private Integer beforeDays;
    private String status;
    private String userName;
    private BigDecimal recentAccuracyRate;
}
