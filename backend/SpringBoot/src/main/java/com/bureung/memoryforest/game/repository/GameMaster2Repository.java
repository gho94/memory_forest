package com.bureung.memoryforest.game.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import com.bureung.memoryforest.game.domain.GameMaster2;
import org.springframework.stereotype.Repository;

@Repository
public interface GameMaster2Repository extends JpaRepository<GameMaster2, String> {
    // TODO : 게임 ID를 substring 으로 비교하는게 좋을지 검토
    @Query(value = "SELECT MAX(game_id) FROM game_master2 WHERE game_id LIKE CONCAT('%', :dateStr, '%')", nativeQuery = true)
    String findMaxGameIdByDate(@Param("dateStr") String dateStr);
}
