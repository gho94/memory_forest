package com.bureung.memoryforest.game.application.impl;

import com.bureung.memoryforest.game.application.GamePlayerAnswerService;
import com.bureung.memoryforest.game.application.GamePlayerService;
import com.bureung.memoryforest.game.application.GameQueryService;
import com.bureung.memoryforest.game.dto.request.GameDashboardRequestDto;
import com.bureung.memoryforest.game.dto.response.GameDashboardResponseDto;
import com.bureung.memoryforest.game.dto.response.GameDashboardStatsResponseDto;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

@Service
@RequiredArgsConstructor
public class GameQueryServiceImpl implements GameQueryService {
    private final GamePlayerService gamePlayerService;
    private final GamePlayerAnswerService gamePlayerAnswerService;

    @Override
    public GameDashboardResponseDto getDashboardStats(GameDashboardRequestDto request) {
        String userId = request.getUserId();

        // endDate 우선순위: 1. param의 endDate, 2. gameId의 end_time, 3. 오늘 날짜
        LocalDate endDate = determineEndDate(request, userId);
        LocalDate startDate = request.getStartDate() != null ? request.getStartDate() : endDate.minusDays(6);

        return GameDashboardResponseDto.builder()
                .stats(buildDashboardStats(userId))
                .weeklyChart(gamePlayerService.getWeeklyAccuracyChart(userId, startDate, endDate))
                .gameList(gamePlayerAnswerService.getTodayGameAnswers(userId, endDate))
                .searchDate(endDate.format(DateTimeFormatter.ofPattern("yyyy년 MM월 dd일", Locale.KOREAN)))
                .build();
    }

    /**
     * endDate 결정 로직
     * 1. request.endDate가 있으면 → request.endDate
     * 2. request.gameId가 있으면 → 해당 게임의 end_time
     * 3. 둘 다 없으면 → 오늘 날짜
     */
    private LocalDate determineEndDate(GameDashboardRequestDto request, String userId) {
        // 1순위: param의 endDate
        if (request.getEndDate() != null) {
            return request.getEndDate();
        }

        // 2순위: gameId가 있으면 해당 게임의 종료일
        if (request.getGameId() != null && !request.getGameId().isEmpty()) {
            LocalDate gameEndDate = gamePlayerService.getGameEndDate(userId, request.getGameId());
            if (gameEndDate != null) {
                return gameEndDate;
            }
        }

        // 3순위: 오늘 날짜
        return LocalDate.now(ZoneId.of("Asia/Seoul"));
    }

    private GameDashboardStatsResponseDto buildDashboardStats(String userId) {
        LocalDate today = LocalDate.now(ZoneId.of("Asia/Seoul"));
        LocalDate yesterday = today.minusDays(1);

        return GameDashboardStatsResponseDto.builder()
                .todayScore(gamePlayerService.getTotalScoreByDate(userId, today))
                .todayAccuracy(gamePlayerService.getAccuracyRateByDate(userId, today))
                .yesterdayScore(gamePlayerService.getTotalScoreByDate(userId, yesterday))
                .yesterdayAccuracy(gamePlayerService.getAccuracyRateByDate(userId, yesterday))
                .weeklyAccuracy(gamePlayerService.getWeeklyAverageAccuracy(userId, today))
                .weeklyParticipation(gamePlayerService.getWeeklyParticipationRate(userId, today))
                .overallAccuracy(gamePlayerService.getOverallAccuracyRate(userId))
                .weeklyAccuracyDiff(calculateWeeklyAccuracyDiff(userId, today))
                .build();
    }

    /**
     * 주간 정답률 차이 계산
     * 이번주(endDate 기준 7일) vs 저번주(그 이전 7일) 정답률 차이
     */
    private BigDecimal calculateWeeklyAccuracyDiff(String userId, LocalDate endDate) {
        // 이번주 정답률 (endDate 기준으로 7일간)
        LocalDate thisWeekStart = endDate.minusDays(6);
        BigDecimal thisWeekAccuracy = gamePlayerService.getWeeklyAverageAccuracy(userId, endDate);

        // 저번주 정답률 (그 이전 7일간)
        LocalDate lastWeekEnd = thisWeekStart.minusDays(1);
        LocalDate lastWeekStart = lastWeekEnd.minusDays(6);
        BigDecimal lastWeekAccuracy = gamePlayerService.getWeeklyAverageAccuracyBetween(userId, lastWeekStart, lastWeekEnd);

        // 차이 계산 (이번주 - 저번주)
        if (thisWeekAccuracy != null && lastWeekAccuracy != null) {
            return thisWeekAccuracy.subtract(lastWeekAccuracy);
        }

        return BigDecimal.ZERO;
    }
}
