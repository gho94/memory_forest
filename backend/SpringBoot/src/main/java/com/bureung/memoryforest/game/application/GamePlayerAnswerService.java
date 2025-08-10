package com.bureung.memoryforest.game.application;

import com.bureung.memoryforest.game.dto.response.GamePlayerDetailResponseDto;

import java.time.LocalDate;
import java.util.List;

public interface GamePlayerAnswerService {
    /**
     * 특정 날짜의 게임 답변 목록 조회
     */
    List<GamePlayerDetailResponseDto> getTodayGameAnswers(String userId, LocalDate targetDate);

    int getCountByGameIdAndPlayerId(String gameId, String playerId);
}
