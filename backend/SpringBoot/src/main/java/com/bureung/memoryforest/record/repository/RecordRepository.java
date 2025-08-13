package com.bureung.memoryforest.record.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import com.bureung.memoryforest.record.domain.Record;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface RecordRepository extends JpaRepository<Record, Integer> {
    List<Record> findByUserIdAndCreatedAtBetweenOrderByCreatedAtDesc(
            String userId, LocalDateTime startDate, LocalDateTime endDate);

    @Query(value = "SELECT CASE WHEN EXISTS(SELECT 1 FROM records WHERE user_id = :userId AND DATE(created_at) = :date) THEN 1 ELSE 0 END",
            nativeQuery = true)
    int existsByUserIdAndCreatedAt(@Param("userId") String userId, @Param("date") LocalDate date);
}
