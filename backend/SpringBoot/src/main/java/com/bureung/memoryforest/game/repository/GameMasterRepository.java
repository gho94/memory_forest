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

    // 특정 날짜의 최대 게임 ID 조회 (게임 ID 생성용)
    @Query("SELECT MAX(g.gameId) FROM GameMaster g WHERE g.gameId LIKE CONCAT('G', :dateStr, '%')")
    String findMaxGameIdByDate(@Param("dateStr") String dateStr);
}