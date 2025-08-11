package com.bureung.memoryforest.game.dto.response;

import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;
import java.util.List;

@Getter
@Builder
public class GamePlayerOverviewResponseDto {
    private Integer totalGames;        // 총 게임 횟수
    private BigDecimal averageAccuracy;    // 평균 정확도
    private List<GameWeeklyAccuracyChartDto> weeklyChart;  // 일주일 차트
    private String searchDate;         // 기준 날짜
}