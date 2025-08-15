package com.bureung.memoryforest.record.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDate;
@Getter
@Builder
@AllArgsConstructor
public class RecordWeeklyScoreChartDto {
    private String dayOfWeek; // 월, 화, 수, 목, 금, 토, 일
    private Integer score;
    private LocalDate date;

    public RecordWeeklyScoreChartDto(LocalDate date, Integer score) {
        this.date = date;
        this.score = score;
        this.dayOfWeek = getDayOfWeekKorean(date);
    }

    private String getDayOfWeekKorean(LocalDate date) {
        if (date == null) return "";

        switch (date.getDayOfWeek()) {
            case MONDAY: return "월";
            case TUESDAY: return "화";
            case WEDNESDAY: return "수";
            case THURSDAY: return "목";
            case FRIDAY: return "금";
            case SATURDAY: return "토";
            case SUNDAY: return "일";
            default: return "";
        }
    }
}
