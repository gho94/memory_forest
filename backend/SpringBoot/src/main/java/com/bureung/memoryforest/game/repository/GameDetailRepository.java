package com.bureung.memoryforest.game.repository;

import com.bureung.memoryforest.game.domain.GameDetail;
import com.bureung.memoryforest.game.domain.GameDetailId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface GameDetailRepository extends JpaRepository<GameDetail, GameDetailId> {

    // 게임 ID와 시퀀스로 조회
    Optional<GameDetail> findByGameIdAndGameSeq(String gameId, Integer gameSeq);

    // 게임 ID로 모든 문제 조회 (순서대로)
    List<GameDetail> findByGameIdOrderByGameOrder(String gameId);

    // 게임 ID로 문제 개수 조회
    long countByGameId(String gameId);

    // 특정 날짜의 최대 게임 ID 조회 (게임 ID 생성용)
    @Query("SELECT MAX(g.gameId) FROM GameDetail g WHERE g.gameId LIKE CONCAT('G', :dateStr, '%')")
    String findMaxGameIdByDate(@Param("dateStr") String dateStr);

    // 특정 게임의 최대 시퀀스 번호 조회
    @Query("SELECT MAX(g.gameSeq) FROM GameDetail g WHERE g.gameId = :gameId")
    Integer findMaxGameSeqByGameId(@Param("gameId") String gameId);

    // AI 분석 상태별 조회
    List<GameDetail> findByAiStatus(String aiStatus);

    // AI 분석 대기 중인 항목들 조회
    @Query("SELECT g FROM GameDetail g WHERE g.aiStatus = 'PENDING' AND g.answerText IS NOT NULL AND g.answerText != ''")
    List<GameDetail> findPendingAIAnalysis();

    // 카테고리별 게임 조회
    List<GameDetail> findByCategoryCodeOrderByGameIdDesc(String categoryCode);

    // 게임 ID로 첫 번째 문제 조회
    @Query("SELECT g FROM GameDetail g WHERE g.gameId = :gameId AND g.gameSeq = 1")
    Optional<GameDetail> findFirstQuestionByGameId(@Param("gameId") String gameId);

    // AI 분석 완료된 게임들 조회
    @Query("SELECT g FROM GameDetail g WHERE g.aiStatus = 'COMPLETED' AND g.wrongOption1 IS NOT NULL")
    List<GameDetail> findCompletedAIAnalysis();

    // 특정 게임에서 AI 분석이 필요한 GameDetail들 조회
    @Query("SELECT g FROM GameDetail g WHERE g.gameId = :gameId AND g.answerText IS NOT NULL AND g.answerText != '' AND (g.aiStatus = 'PENDING' OR g.aiStatus = 'FAILED')")
    List<GameDetail> findByGameIdAndNeedingAIAnalysis(@Param("gameId") String gameId);
}