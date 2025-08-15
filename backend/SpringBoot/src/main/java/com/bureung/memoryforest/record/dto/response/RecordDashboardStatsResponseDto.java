package com.bureung.memoryforest.record.dto.response;


import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;

@Getter
@Builder
public class RecordDashboardStatsResponseDto {
    private Integer todayScore;           // 오늘 점수
    private Integer yesterdayScore;       // 어제 점수
    private BigDecimal weeklyScore;    // 일주일 평균점수
    private BigDecimal weeklyParticipation; // 이번주 참여율
    private BigDecimal overallScore;   // 전체 평균점수
    private BigDecimal weeklyScoreDiff; // 주간 평균점수 차이 (이번주 - 저번주)
}
