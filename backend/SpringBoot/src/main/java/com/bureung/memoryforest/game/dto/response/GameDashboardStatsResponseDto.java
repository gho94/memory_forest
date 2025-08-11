package com.bureung.memoryforest.game.dto.response;

import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;

@Getter
@Builder
public class GameDashboardStatsResponseDto {
    private Integer todayScore;           // 오늘 점수
    private BigDecimal todayAccuracy;     // 오늘 정답률
    private Integer yesterdayScore;       // 어제 점수
    private BigDecimal yesterdayAccuracy; // 어제 정답률
    private BigDecimal weeklyAccuracy;    // 일주일 정답률
    private BigDecimal weeklyParticipation; // 이번주 참여율
    private BigDecimal overallAccuracy;   // 전체 정답률
    private BigDecimal weeklyAccuracyDiff; // 주간 정답률 차이 (이번주 - 저번주)
}