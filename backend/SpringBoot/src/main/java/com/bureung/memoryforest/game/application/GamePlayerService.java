package com.bureung.memoryforest.game.application;

import com.bureung.memoryforest.game.domain.GamePlayer;
import com.bureung.memoryforest.game.dto.response.GameWeeklyAccuracyChartDto;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

//leb. Recorder가 게임을 실제 플레이할 때 처리하는 로직 (퀴즈 응답, 채점 등)
public interface GamePlayerService {
    Optional<GamePlayer> getGamesByGameIdAndPlayerId(String gameId, String playerId);

    /**
     * 주간 정답률 차트 데이터 조회
     */
    List<GameWeeklyAccuracyChartDto> getWeeklyAccuracyChart(String userId, LocalDate startDate, LocalDate endDate);

    /**
     * 특정 날짜의 총 점수 조회
     */
    Integer getTotalScoreByDate(String userId, LocalDate date);

    /**
     * 특정 날짜의 정답률 조회
     */
    BigDecimal getAccuracyRateByDate(String userId, LocalDate date);

    /**
     * 주간 평균 정답률 조회 (endDate 기준 7일간)
     */
    BigDecimal getWeeklyAverageAccuracy(String userId, LocalDate endDate);

    /**
     * 기간별 평균 정답률 조회
     */
    BigDecimal getWeeklyAverageAccuracyBetween(String userId, LocalDate startDate, LocalDate endDate);

    /**
     * 주간 참여율 조회
     */
    BigDecimal getWeeklyParticipationRate(String userId, LocalDate endDate);

    /**
     * 전체 정답률 조회
     */
    BigDecimal getOverallAccuracyRate(String userId);

    /**
     * 게임 종료 날짜 조회
     */
    LocalDate getGameEndDate(String userId, String gameId);

    /**
     * 진행중인 게임 조회
     */
    Optional<GamePlayer> getInProgressGameByPlayerId(String playerId);

    /**
     * 가장 최근에 푼 게임 조회
     */
    Optional<GamePlayer> getMostRecentCompletedGameByPlayerId(String playerId);
}
