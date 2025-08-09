package com.bureung.memoryforest.game.repository;

import com.bureung.memoryforest.game.domain.GameMaster;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface GameMasterRepository extends JpaRepository<GameMaster, String> {

    // 전체 게임 조회 (생성일 역순)
    List<GameMaster> findAllByOrderByCreatedAtDesc();

    // 난이도별 게임 조회
    List<GameMaster> findByDifficultyLevelCodeOrderByCreatedAtDesc(String difficultyLevelCode);

    // 상태별 게임 조회
    List<GameMaster> findByCreationStatusCodeOrderByCreatedAtDesc(String creationStatusCode);

    // 생성자별 게임 조회
    List<GameMaster> findByCreatedByOrderByCreatedAtDesc(String createdBy);

    List<GameMaster> findByGameNameContaining(String gameName);

    Optional<GameMaster> findByGameId(String gameId);

    // TODO : 게임 ID를 substring 으로 비교하는게 좋을지 검토
    @Query(value = "SELECT MAX(game_id) FROM game_master WHERE game_id LIKE CONCAT('G', :dateStr, '%')", nativeQuery = true)
    String findMaxGameIdByDate(@Param("dateStr") String dateStr);

    @Query("SELECT gm.gameCount FROM GameMaster gm WHERE gm.gameId = :gameId")
    Optional<Integer> findGameCountByGameId(String gameId);

    // 플레이어가 한 번도 안 푼 가장 오래된 게임 찾기
    @Query("""
        SELECT gm FROM GameMaster gm 
        WHERE NOT EXISTS (
            SELECT 1 FROM GamePlayer gp 
            WHERE gp.id.gameId = gm.gameId AND gp.id.playerId = :playerId
        )
        ORDER BY gm.createdAt ASC
        """)
    Optional<GameMaster> findOldestUnplayedGameByPlayerId(@Param("playerId") String playerId);
}