package com.bureung.memoryforest.record.application;

import com.bureung.memoryforest.record.dto.request.RecordDashboardRequestDto;
import com.bureung.memoryforest.record.dto.response.RecordDashboardResponseDto;
import com.bureung.memoryforest.record.dto.response.RecordListResponseDto;
import com.bureung.memoryforest.record.dto.response.RecordWeeklyScoreChartDto;

import java.time.LocalDate;
import java.util.List;

public interface RecordService {

    void saveRecord(Integer fileId, String text, Integer duration, String userId);
    List<RecordListResponseDto> getRecordsByYearMonth(String userId, int year, int month);
    boolean hasRecordToday(String userId);
    RecordDashboardResponseDto getDashboardStats(RecordDashboardRequestDto request);
    List<RecordWeeklyScoreChartDto> getWeeklyScoreChart(String userId, LocalDate startDate, LocalDate endDate);
}
