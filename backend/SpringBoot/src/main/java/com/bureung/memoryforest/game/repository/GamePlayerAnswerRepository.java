package com.bureung.memoryforest.game.repository;

import com.bureung.memoryforest.game.domain.GamePlayerAnswer;
import com.bureung.memoryforest.game.domain.GamePlayerAnswerId;
import com.bureung.memoryforest.game.dto.response.GamePlayerDetailResponseDto;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface GamePlayerAnswerRepository extends JpaRepository<GamePlayerAnswer, GamePlayerAnswerId> {
    @Query("SELECT new com.bureung.memoryforest.game.dto.response.GamePlayerDetailResponseDto(" +
            "gpa.id.gameId, " +
            "gpa.id.gameSeq," +
            "gpa.selectedOption, " +
            "gpa.isCorrect, " +
            "gm.gameName, " +
            "gpa.scoreEarned, " +
            "gd.answerText, " +
            "gd.wrongOption1, " +
            "gd.wrongOption2, " +
            "gd.wrongOption3, " +
            "gd.filePath, " +
            "'완료') " +
            "FROM GamePlayerAnswer gpa " +
            "JOIN GameDetail gd ON gpa.id.gameId = gd.gameId AND gpa.id.gameSeq = gd.gameSeq " +
            "JOIN GameMaster gm ON gpa.id.gameId = gm.gameId " +
            "JOIN GamePlayer gp ON gp.id.playerId = gpa.id.playerId " +
            "WHERE gpa.id.playerId = :userId " +
            "AND DATE(gp.endTime) = :targetDate " +
            "ORDER BY gp.endTime DESC")
    List<GamePlayerDetailResponseDto> findTodayGameAnswers(@Param("userId") String userId,
                                                           @Param("targetDate") LocalDate targetDate);

    // 특정 게임에 플레이어가 참여한 적이 있는지 확인
    Optional<Integer> countByIdGameIdAndIdPlayerId(String gameId, String playerId);
}
