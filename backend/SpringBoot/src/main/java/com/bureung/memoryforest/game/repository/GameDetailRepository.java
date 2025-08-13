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
    
    // 게임 ID로 조회 (기본)
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
    
    // ========== AI 상태 코드 관련 조회 메서드들 ==========
    
    // AI 상태 코드별 조회
    List<GameDetail> findByAiStatusCode(String aiStatusCode);
    
    // AI 상태 코드별 개수 조회 (추가)
    long countByAiStatusCode(String aiStatusCode);
    
    // AI 분석 대기 중인 항목들 조회
    @Query("SELECT g FROM GameDetail g WHERE g.aiStatusCode = 'B20005' AND g.answerText IS NOT NULL AND g.answerText != ''")
    List<GameDetail> findPendingAIAnalysis();
    
    // AI 분석 대기 중인 항목 개수 조회
    @Query("SELECT COUNT(g) FROM GameDetail g WHERE g.aiStatusCode = 'B20005' AND g.answerText IS NOT NULL AND g.answerText != ''")
    long countPendingAIAnalysis();
    
    // AI 분석 완료된 게임들 조회
    @Query("SELECT g FROM GameDetail g WHERE g.aiStatusCode = 'B20007' AND g.wrongOption1 IS NOT NULL")
    List<GameDetail> findCompletedAIAnalysis();
    
    // AI 분석 완료된 게임 개수 조회
    @Query("SELECT COUNT(g) FROM GameDetail g WHERE g.aiStatusCode = 'B20007' AND g.wrongOption1 IS NOT NULL")
    long countCompletedAIAnalysis();
    
    // AI 분석 실패한 게임들 조회
    @Query("SELECT g FROM GameDetail g WHERE g.aiStatusCode = 'B20008'")
    List<GameDetail> findFailedAIAnalysis();
    
    // AI 분석 실패한 게임 개수 조회
    @Query("SELECT COUNT(g) FROM GameDetail g WHERE g.aiStatusCode = 'B20008'")
    long countFailedAIAnalysis();
    
    // AI 분석 진행 중인 게임들 조회
    @Query("SELECT g FROM GameDetail g WHERE g.aiStatusCode = 'B20006'")
    List<GameDetail> findProcessingAIAnalysis();
    
    // AI 분석 진행 중인 게임 개수 조회
    @Query("SELECT COUNT(g) FROM GameDetail g WHERE g.aiStatusCode = 'B20006'")
    long countProcessingAIAnalysis();
    
    // ========== 기타 조회 메서드들 ==========
    
    // 게임 ID로 첫 번째 문제 조회
    @Query("SELECT g FROM GameDetail g WHERE g.gameId = :gameId AND g.gameSeq = 1")
    Optional<GameDetail> findFirstQuestionByGameId(@Param("gameId") String gameId);
    
    // 특정 게임에서 AI 분석이 필요한 GameDetail들 조회
    @Query("SELECT g FROM GameDetail g WHERE g.gameId = :gameId AND g.answerText IS NOT NULL AND g.answerText != '' AND (g.aiStatusCode = 'B20005' OR g.aiStatusCode = 'B20008')")
    List<GameDetail> findByGameIdAndNeedingAIAnalysis(@Param("gameId") String gameId);
    
    // 최근 처리된 AI 분석 개수 조회
    @Query("SELECT COUNT(g) FROM GameDetail g WHERE g.aiProcessedAt >= :dateTime")
    Long countRecentlyProcessed(@Param("dateTime") LocalDateTime dateTime);
    
    // ========== 통계 관련 조회 메서드들 ==========
    
    // AI 상태별 개수 집계 (상태 코드 기준)
    @Query("SELECT g.aiStatusCode, COUNT(g) FROM GameDetail g GROUP BY g.aiStatusCode")
    List<Object[]> findAiStatusCodeCounts();
    
    // 난이도별 AI 상태별 개수 집계 (상태 코드 기준)
    @Query("""
        SELECT gd.aiStatusCode, COUNT(gd)
        FROM GameDetail gd 
        JOIN GameMaster gm ON gd.gameId = gm.gameId
        WHERE gm.difficultyLevelCode = :difficultyCode
        GROUP BY gd.aiStatusCode
        """)
    List<Object[]> findAiStatusCodeCountsByDifficulty(@Param("difficultyCode") String difficultyCode);
    
    // 답변 텍스트가 있는 전체 게임 개수
    @Query("SELECT COUNT(g) FROM GameDetail g WHERE g.answerText IS NOT NULL AND g.answerText != ''")
    long countGamesWithAnswerText();
    
    // 특정 날짜 이후 처리된 게임 개수 (상태별)
    @Query("SELECT g.aiStatusCode, COUNT(g) FROM GameDetail g WHERE g.aiProcessedAt >= :dateTime GROUP BY g.aiStatusCode")
    List<Object[]> countProcessedGamesByStatusSince(@Param("dateTime") LocalDateTime dateTime);
    
    // ========== 답변 텍스트 기준 조회 ==========
    
    // 특정 답변 텍스트를 가진 게임들 조회
    List<GameDetail> findByAnswerText(String answerText);
    
    // 특정 답변 텍스트를 가진 게임 개수 조회
    long countByAnswerText(String answerText);
    
    // 특정 답변 텍스트와 AI 상태를 가진 게임들 조회
    List<GameDetail> findByAnswerTextAndAiStatusCode(String answerText, String aiStatusCode);
    
    // 특정 답변 텍스트와 AI 상태를 가진 게임 개수 조회
    long countByAnswerTextAndAiStatusCode(String answerText, String aiStatusCode);
    
    // ========== 점수 관련 조회 메서드들 ==========
    
    /**
     * 특정 게임의 특정 컬럼의 점수 조회
     * @param gameId 게임 ID
     * @param gameSeq 게임 시퀀스
     * @param columnName 점수 컬럼명 ("wrong_score_1", "wrong_score_2", "wrong_score_3")
     * @return 점수 (정수)
     */
    @Query(value = """
        SELECT 
            CASE :columnName
                WHEN 'wrong_score_1' THEN CAST(wrong_score_1 AS SIGNED)
                WHEN 'wrong_score_2' THEN CAST(wrong_score_2 AS SIGNED)  
                WHEN 'wrong_score_3' THEN CAST(wrong_score_3 AS SIGNED)
                ELSE 0
            END as score
        FROM game_detail 
        WHERE game_id = :gameId AND game_seq = :gameSeq
        """, nativeQuery = true)
    Optional<Integer> findScoreByColumn(@Param("gameId") String gameId, 
                                       @Param("gameSeq") int gameSeq, 
                                       @Param("columnName") String columnName);
    
    /**
     * 특정 게임의 모든 점수 조회
     */
    @Query("SELECT g.wrongScore1, g.wrongScore2, g.wrongScore3 FROM GameDetail g WHERE g.gameId = :gameId AND g.gameSeq = :gameSeq")
    Optional<Object[]> findAllScoresByGameIdAndSeq(@Param("gameId") String gameId, @Param("gameSeq") int gameSeq);
    
    /**
     * 특정 게임의 wrong_score_1 조회
     */
    @Query("SELECT g.wrongScore1 FROM GameDetail g WHERE g.gameId = :gameId AND g.gameSeq = :gameSeq")
    Optional<Double> findWrongScore1(@Param("gameId") String gameId, @Param("gameSeq") int gameSeq);
    
    /**
     * 특정 게임의 wrong_score_2 조회
     */
    @Query("SELECT g.wrongScore2 FROM GameDetail g WHERE g.gameId = :gameId AND g.gameSeq = :gameSeq")
    Optional<Double> findWrongScore2(@Param("gameId") String gameId, @Param("gameSeq") int gameSeq);
    
    /**
     * 특정 게임의 wrong_score_3 조회
     */
    @Query("SELECT g.wrongScore3 FROM GameDetail g WHERE g.gameId = :gameId AND g.gameSeq = :gameSeq")
    Optional<Double> findWrongScore3(@Param("gameId") String gameId, @Param("gameSeq") int gameSeq);
    
    // ========== 오답 옵션 관련 조회 메서드들 ==========
    
    /**
     * 특정 게임의 모든 오답 옵션 조회
     */
    @Query("SELECT g.wrongOption1, g.wrongOption2, g.wrongOption3 FROM GameDetail g WHERE g.gameId = :gameId AND g.gameSeq = :gameSeq")
    Optional<Object[]> findAllWrongOptionsByGameIdAndSeq(@Param("gameId") String gameId, @Param("gameSeq") int gameSeq);
    
    /**
     * 특정 컬럼의 오답 옵션 조회
     */
    @Query(value = """
        SELECT 
            CASE :columnName
                WHEN 'wrong_option_1' THEN wrong_option_1
                WHEN 'wrong_option_2' THEN wrong_option_2
                WHEN 'wrong_option_3' THEN wrong_option_3
                ELSE ''
            END as option_text
        FROM game_detail 
        WHERE game_id = :gameId AND game_seq = :gameSeq
        """, nativeQuery = true)
    Optional<String> findWrongOptionByColumn(@Param("gameId") String gameId, 
                                           @Param("gameSeq") int gameSeq, 
                                           @Param("columnName") String columnName);
}