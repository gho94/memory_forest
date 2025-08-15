package com.bureung.memoryforest.record.repository;

import com.bureung.memoryforest.record.dto.response.RecordListResponseDto;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import com.bureung.memoryforest.record.domain.Record;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface RecordRepository extends JpaRepository<Record, Integer> {
    List<Record> findByUserIdAndCreatedAtBetweenOrderByCreatedAtDesc(
            String userId, LocalDateTime startDate, LocalDateTime endDate);

    @Query(value = "SELECT CASE WHEN EXISTS(SELECT 1 FROM records WHERE user_id = :userId AND DATE(created_at) = :date) THEN 1 ELSE 0 END",
            nativeQuery = true)
    int existsByUserIdAndCreatedAt(@Param("userId") String userId, @Param("date") LocalDate date);

    @Query("SELECT r.score FROM Record r " +
            "WHERE r.userId = :userId " +
            "AND DATE(r.createdAt) = :date")
    Optional<Integer> findScoreByDate(@Param("userId") String userId, @Param("date") LocalDate date);

    @Query("SELECT AVG(r.score) FROM Record r " +
            "WHERE r.userId = :userId " +
            "AND DATE(r.createdAt) BETWEEN :startDate AND :endDate " +
            "AND r.score IS NOT NULL")
    BigDecimal findWeeklyAverageScore(@Param("userId") String userId,
                                         @Param("startDate") LocalDate startDate,
                                         @Param("endDate") LocalDate endDate);


    // Repository 메서드
    @Query("SELECT CASE WHEN COUNT(r) > 0 THEN 100.0 ELSE 0.0 END " +
            "FROM Record r " +
            "WHERE r.userId = :userId " +
            "AND DATE(r.createdAt) >= :startDate " +
            "AND DATE(r.createdAt) <= :endDate")
    BigDecimal findWeeklyParticipationRate(@Param("userId") String userId,
                                           @Param("startDate") LocalDate startDate,
                                           @Param("endDate") LocalDate endDate);

    @Query("SELECT AVG(r.score) FROM Record r WHERE r.userId = :userId")
    BigDecimal findAverageScoreByUserId(@Param("userId") String userId);

    @Query(value = "SELECT " +
            "  DATE(r.created_at) as date, " +
            "  r.score as score " +
            "FROM records r " +
            "WHERE r.user_id = :userId " +
            "  AND DATE(r.created_at) BETWEEN :startDate AND :endDate " +
            "  AND r.score IS NOT NULL " +
            "ORDER BY DATE(r.created_at)", nativeQuery = true)
    List<Object[]> findWeeklyScoreChartRaw(@Param("userId") String userId,
                                              @Param("startDate") LocalDate startDate,
                                              @Param("endDate") LocalDate endDate);

    @Query("SELECT new com.bureung.memoryforest.record.dto.response.RecordListResponseDto(" +
            "r.recordId, " +
            "r.fileId, " +
            "r.text, " +
            "r.duration, " +
            "r.createdAt) " +
            "FROM Record r WHERE r.userId = :userId AND DATE(r.createdAt) = :endDate " +
            "ORDER BY r.createdAt DESC LIMIT 1")
    RecordListResponseDto getRecordEntities(@Param("userId") String userId,
                                                  @Param("endDate") LocalDate endDate);

}
