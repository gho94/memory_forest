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

    // JpaRepository에서 기본 제공하는 findById 사용하면 되므로 findByGameId는 불필요
    // Optional<GameMaster> findByGameId(String gameId); 제거

    // 난이도별 게임 조회
    List<GameMaster> findByDifficultyLevelOrderByCreatedAtDesc(String difficultyLevel);

    // 생성 상태별 게임 조회
    List<GameMaster> findByCreationStatusCodeOrderByCreatedAtDesc(String creationStatusCode);

    // 생성자별 게임 조회
    List<GameMaster> findByCreatedByOrderByCreatedAtDesc(String createdBy);

    // 특정 날짜의 최대 게임 ID 조회 (게임 ID 생성용)
    @Query("SELECT MAX(g.gameId) FROM GameMaster g WHERE g.gameId LIKE CONCAT('G', :dateStr, '%')")
    String findMaxGameIdByDate(@Param("dateStr") String dateStr);

    // 전체 게임 목록 (최신순) - JpaRepository의 findAll() 사용하거나 아래처럼 정의
    List<GameMaster> findAllByOrderByCreatedAtDesc();

    // 게임 개수별 조회
    List<GameMaster> findByGameCountOrderByCreatedAtDesc(Integer gameCount);

    // 게임명으로 검색
    List<GameMaster> findByGameNameContainingIgnoreCaseOrderByCreatedAtDesc(String gameName);

    // 완료된 게임만 조회
    @Query("SELECT g FROM GameMaster g WHERE g.creationStatusCode = 'COMPLETED' ORDER BY g.createdAt DESC")
    List<GameMaster> findCompletedGames();

    // 공개된 게임만 조회
    @Query("SELECT g FROM GameMaster g WHERE g.creationStatusCode = 'PUBLISHED' ORDER BY g.createdAt DESC")
    List<GameMaster> findPublishedGames();
}