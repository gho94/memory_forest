package com.bureung.memoryforest.game.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;
import java.time.LocalDate;

@Getter
@Builder
@AllArgsConstructor
public class GameWeeklyAccuracyChartDto {
    private String dayOfWeek; // 월, 화, 수, 목, 금, 토, 일
    private BigDecimal accuracy;
    private LocalDate date;

    public GameWeeklyAccuracyChartDto(LocalDate date, BigDecimal accuracy) {
        this.date = date;
        this.accuracy = accuracy;
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