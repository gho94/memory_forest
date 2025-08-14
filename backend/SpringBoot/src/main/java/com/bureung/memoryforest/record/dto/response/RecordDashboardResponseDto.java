package com.bureung.memoryforest.record.dto.response;
import lombok.Builder;
import lombok.Getter;

import java.util.List;

@Getter
@Builder
public class RecordDashboardResponseDto {
    private RecordDashboardStatsResponseDto stats;
    private List<RecordWeeklyScoreChartDto> weeklyChart;
    private RecordListResponseDto record;
    private String searchDate; // "2025년 08월 07일"
}
