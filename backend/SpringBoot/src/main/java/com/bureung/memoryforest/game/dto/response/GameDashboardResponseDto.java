package com.bureung.memoryforest.game.dto.response;

import lombok.Builder;
import lombok.Getter;

import java.util.List;

@Getter
@Builder
public class GameDashboardResponseDto {
    private GameDashboardStatsResponseDto stats;
    private List<GameWeeklyAccuracyChartDto> weeklyChart;
    private List<GamePlayerDetailResponseDto> gameList;
    private String searchDate; // "2025년 08월 07일"
}