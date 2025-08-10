package com.bureung.memoryforest.game.application.impl;

import com.bureung.memoryforest.game.application.GamePlayerAnswerService;
import com.bureung.memoryforest.game.application.GamePlayerService;
import com.bureung.memoryforest.game.domain.GamePlayer;
import com.bureung.memoryforest.game.dto.response.GamePlayResultResponseDto;
import com.bureung.memoryforest.game.dto.response.GameWeeklyAccuracyChartDto;
import com.bureung.memoryforest.game.repository.GamePlayerRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class GamePlayerServiceImpl implements GamePlayerService {
    private final GamePlayerRepository gamePlayerRepository;
    private final GamePlayerAnswerService gamePlayerAnswerService;

    @Override
    public Optional<GamePlayer> getGamesByGameIdAndPlayerId(String gameId, String playerId) {
        return gamePlayerRepository.findByIdGameIdAndIdPlayerId(gameId, playerId);
    }

    @Override
    public List<GameWeeklyAccuracyChartDto> getWeeklyAccuracyChart(String userId, LocalDate startDate, LocalDate endDate) {
        log.info("주간 차트 인자: startDate={}, endDate={}, userId={}",
                startDate, endDate, userId);
        List<Object[]> rawResults = gamePlayerRepository.findWeeklyAccuracyChartRaw(userId, startDate, endDate);
        return rawResults.stream()
                .map(row -> {
                    LocalDate date = ((java.sql.Date) row[0]).toLocalDate();
                    BigDecimal accuracy = (BigDecimal) row[1];
                    return new GameWeeklyAccuracyChartDto(date, accuracy);
                })
                .collect(Collectors.toList());
    }

    @Override
    public Integer getTotalScoreByDate(String userId, LocalDate date) {
        log.info("게임 총 점수 : userId={}, date={}",
                userId, date);
        return gamePlayerRepository.findTotalScoreByDate(userId, date).orElse(0);
    }

    @Override
    public BigDecimal getAccuracyRateByDate(String userId, LocalDate date) {
        return gamePlayerRepository.findAccuracyRateByDate(userId, date)
                .orElse(BigDecimal.ZERO);
    }

    @Override
    public BigDecimal getWeeklyAverageAccuracy(String userId, LocalDate endDate) {
        LocalDate startDate = endDate.minusDays(6);
        return getWeeklyAverageAccuracyBetween(userId, startDate, endDate);
    }

    @Override
    public BigDecimal getWeeklyAverageAccuracyBetween(String userId, LocalDate startDate, LocalDate endDate) {
        log.info("게임 주간 정확도 차이 : userId={}, startDate={}, endDate={}",
                userId, startDate, endDate);
        BigDecimal result = gamePlayerRepository.findWeeklyAverageAccuracy(userId, startDate, endDate);
        return result != null ? result : BigDecimal.ZERO;
    }

    @Override
    public BigDecimal getWeeklyParticipationRate(String userId, LocalDate endDate) {
        // 이번주 시작 (일요일 기준)
        LocalDate startOfWeek = endDate.minusDays(endDate.getDayOfWeek().getValue() % 7);
        BigDecimal result = gamePlayerRepository.findWeeklyParticipationRate(userId, startOfWeek, endDate);
        return result != null ? result : BigDecimal.ZERO;
    }

    @Override
    public BigDecimal getOverallAccuracyRate(String userId) {
        BigDecimal result = gamePlayerRepository.findOverallAccuracyRate(userId);
        return result != null ? result : BigDecimal.ZERO;
    }

    @Override
    public LocalDate getGameEndDate(String userId, String gameId) {
        return gamePlayerRepository.findGameEndDate(userId, gameId).orElse(null);
    }

    @Override
    public Optional<GamePlayer> getInProgressGameByPlayerId (String playerId){
        return gamePlayerRepository.findByIdPlayerIdAndEndTimeIsNullAndStartTimeIsNotNull(playerId);
    }

    @Override
    public Optional<GamePlayer> getMostRecentCompletedGameByPlayerId(String playerId){
        return gamePlayerRepository.findFirstByIdPlayerIdAndEndTimeIsNotNullOrderByEndTimeDesc(playerId);
    }

    @Override
    public GamePlayResultResponseDto getGamePlayResult(String gameId, String playerId){
        GamePlayResultResponseDto response = gamePlayerAnswerService.getGamePlayAnswerResultSummary(gameId, playerId).orElseThrow(() -> new RuntimeException("게임을 찾을 수 없습니다: " + gameId));
        GamePlayer gamePlayer = getGamesByGameIdAndPlayerId(gameId, playerId).orElseThrow();
        gamePlayer.setTotalScore(response.getTotalScore());
        gamePlayer.setAccuracyRate(response.getAccuracyRate());
        gamePlayer.setDurationSeconds(response.getDurationSeconds());
        gamePlayer.setCorrectCount(response.getCorrectCount());
        gamePlayerRepository.save(gamePlayer);
        return response;
    }
}
