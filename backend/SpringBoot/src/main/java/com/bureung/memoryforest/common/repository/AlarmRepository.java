package com.bureung.memoryforest.common.repository;

import com.bureung.memoryforest.common.domain.Alarm;
import com.bureung.memoryforest.common.dto.response.AlarmResponseDto;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AlarmRepository extends JpaRepository<Alarm, Integer> {
    /**
     * 세션 유저 ID 기준으로 알람 조회 (game_master.created_by 조인)
     * game_player와도 조인해서 total_score까지 가져옴
     */
    @Query("SELECT new com.bureung.memoryforest.common.dto.response.AlarmResponseDto(" +
            "a.alarmId, a.game.id.gameId, a.isRead, a.createdAt, a.game.totalScore, " +
            "a.game.id.playerId, u.userName) " +
            "FROM Alarm a " +
            "JOIN User u ON a.game.id.playerId = u.userId " +
            "JOIN GameMaster gm ON a.game.id.gameId = gm.gameId " +
            "WHERE gm.createdBy = :userId " +
            "ORDER BY a.createdAt DESC")
    List<AlarmResponseDto> findAlarmsByFamilyUserId(@Param("userId") String userId);

    /**
     * 알람 읽음 처리
     */
    @Modifying
    @Query("UPDATE Alarm a SET a.isRead = 'Y' WHERE a.alarmId = :alarmId")
    int markAsReadById(@Param("alarmId") Integer alarmId);
}