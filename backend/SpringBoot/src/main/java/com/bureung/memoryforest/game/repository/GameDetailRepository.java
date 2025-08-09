package com.bureung.memoryforest.game.repository;

import com.bureung.memoryforest.game.domain.GameDetail;
import com.bureung.memoryforest.game.domain.GameDetailId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface GameDetailRepository extends JpaRepository<GameDetail, GameDetailId> {
    List<GameDetail> findByGameId(String gameId);
    
    // 게임 ID로 시퀀스 순으로 조회
    List<GameDetail> findByGameIdOrderByGameSeq(String gameId);
    
    // 게임 ID와 시퀀스로 단건 조회
    @Query("SELECT g FROM GameDetail g WHERE g.gameId = :gameId AND g.gameSeq = :gameSeq")
    Optional<GameDetail> findByGameIdAndGameSeq(@Param("gameId") String gameId, @Param("gameSeq") Integer gameSeq);
    
    // 게임 ID로 모든 문제 조회 (게임 순서대로)
    List<GameDetail> findByGameIdOrderByGameOrder(String gameId);
    
    // 게임 ID로 문제 개수 조회
    long countByGameId(String gameId);
    
    // AI 분석 상태별 조회
    List<GameDetail> findByAiStatusCode(String aiStatus);
    
    // AI 분석 대기 중인 항목들 조회
    @Query("SELECT g FROM GameDetail g WHERE g.aiStatusCode = 'PENDING' AND g.answerText IS NOT NULL AND g.answerText != ''")
    List<GameDetail> findPendingAIAnalysis();
        
    // 게임 ID로 첫 번째 문제 조회
    @Query("SELECT g FROM GameDetail g WHERE g.gameId = :gameId AND g.gameSeq = 1")
    Optional<GameDetail> findFirstQuestionByGameId(@Param("gameId") String gameId);
    
    // AI 분석 완료된 게임들 조회
    @Query("SELECT g FROM GameDetail g WHERE g.aiStatusCode = 'COMPLETED' AND g.wrongOption1 IS NOT NULL")
    List<GameDetail> findCompletedAIAnalysis();
    
    // 특정 게임에서 AI 분석이 필요한 GameDetail들 조회
    @Query("SELECT g FROM GameDetail g WHERE g.gameId = :gameId AND g.answerText IS NOT NULL AND g.answerText != '' AND (g.aiStatusCode = 'PENDING' OR g.aiStatusCode = 'FAILED')")
    List<GameDetail> findByGameIdAndNeedingAIAnalysis(@Param("gameId") String gameId);
    
    // 최근 처리된 AI 분석 개수 조회
    @Query("SELECT COUNT(g) FROM GameDetail g WHERE g.aiProcessedAt >= :dateTime")
    Long countRecentlyProcessed(@Param("dateTime") LocalDateTime dateTime);
    
    // AI 상태별 개수 집계
    @Query("SELECT g.aiStatusCode, COUNT(g) FROM GameDetail g GROUP BY g.aiStatusCode")
    List<Object[]> findAiStatusCodeCounts();
    
    // 난이도별 AI 상태별 개수 집계 (GameMaster와 조인)
    @Query("""
        SELECT gd.aiStatusCode, COUNT(gd)
        FROM GameDetail gd 
        JOIN GameMaster gm ON gd.gameId = gm.gameId
        WHERE gm.difficultyLevelCode = :difficultyCode
        GROUP BY gd.aiStatusCode
        """)
    List<Object[]> findAiStatusCodeCountsByDifficulty(@Param("difficultyCode") String difficultyCode);
}