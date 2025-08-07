package com.bureung.memoryforest.game.repository;

import com.bureung.memoryforest.game.domain.GamePlayer;
import com.bureung.memoryforest.game.domain.GamePlayerId;
import com.bureung.memoryforest.game.dto.response.GameWeeklyAccuracyChartDto;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface GamePlayerRepository extends JpaRepository<GamePlayer, GamePlayerId> {
    Optional<GamePlayer> findByIdGameIdAndIdPlayerId(String gameId, String playerId);

    @Query("SELECT gp.totalScore FROM GamePlayer gp " +
            "WHERE gp.id.playerId = :userId " +
            "AND DATE(gp.endTime) = :date")
    Optional<Integer> findTotalScoreByDate(@Param("userId") String userId, @Param("date") LocalDate date);

    @Query("SELECT gp.accuracyRate FROM GamePlayer gp " +
            "WHERE gp.id.playerId = :userId " +
            "AND DATE(gp.endTime) = :date")
    Optional<BigDecimal> findAccuracyRateByDate(@Param("userId") String userId, @Param("date") LocalDate date);

    @Query("SELECT AVG(gp.accuracyRate) FROM GamePlayer gp " +
            "WHERE gp.id.playerId = :userId " +
            "AND DATE(gp.endTime) BETWEEN :startDate AND :endDate " +
            "AND gp.accuracyRate IS NOT NULL")
    BigDecimal findWeeklyAverageAccuracy(@Param("userId") String userId,
                                         @Param("startDate") LocalDate startDate,
                                         @Param("endDate") LocalDate endDate);

    @Query(value = "SELECT " +
            "  DATE(gp.end_time) as date, " +
            "  AVG(gp.accuracy_rate) as accuracy " +
            "FROM game_player gp " +
            "WHERE gp.player_id = :userId " +
            "  AND DATE(gp.end_time) BETWEEN :startDate AND :endDate " +
            "  AND gp.accuracy_rate IS NOT NULL " +
            "GROUP BY DATE(gp.end_time) " +
            "ORDER BY DATE(gp.end_time)", nativeQuery = true)
    List<Object[]> findWeeklyAccuracyChartRaw(@Param("userId") String userId,
                                              @Param("startDate") LocalDate startDate,
                                              @Param("endDate") LocalDate endDate);

    @Query(value =
            "SELECT " +
                    "  (SUM(answered_count) * 100.0 / SUM(total_count)) as participation_rate " +
                    "FROM ( " +
                    "  SELECT " +
                    "    DATE(gp.end_time) as game_date, " +
                    "    COUNT(gpa.game_seq) as answered_count, " +
                    "    gm.game_count as total_count " +
                    "  FROM game_player gp " +
                    "  JOIN game_master gm ON gp.game_id = gm.game_id " +
                    "  LEFT JOIN game_player_answer gpa ON gp.game_id = gpa.game_id AND gp.player_id = gpa.player_id " +
                    "  WHERE gp.player_id = :userId " +
                    "  AND DATE(gp.end_time) BETWEEN :startDate AND :endDate " +
                    "  GROUP BY DATE(gp.end_time), gm.game_count " +
                    ") as daily_stats", nativeQuery = true)
    BigDecimal findWeeklyParticipationRate(@Param("userId") String userId,
                                           @Param("startDate") LocalDate startDate,
                                           @Param("endDate") LocalDate endDate);

    @Query("SELECT AVG(gp.accuracyRate) FROM GamePlayer gp " +
            "WHERE gp.id.playerId = :userId " +
            "AND gp.accuracyRate IS NOT NULL")
    BigDecimal findOverallAccuracyRate(@Param("userId") String userId);

    @Query("SELECT DATE(gp.endTime) FROM GamePlayer gp " +
            "WHERE gp.id.playerId = :userId " +
            "AND gp.id.gameId = :gameId")
    Optional<LocalDate> findGameEndDate(@Param("userId") String userId,
                                        @Param("gameId") String gameId);
}
