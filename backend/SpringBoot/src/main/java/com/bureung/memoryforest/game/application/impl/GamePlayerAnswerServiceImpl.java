package com.bureung.memoryforest.game.application.impl;

import com.bureung.memoryforest.game.application.GamePlayerAnswerService;
import com.bureung.memoryforest.game.dto.response.GamePlayerDetailResponseDto;
import com.bureung.memoryforest.game.repository.GamePlayerAnswerRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
@RequiredArgsConstructor
public class GamePlayerAnswerServiceImpl implements GamePlayerAnswerService {

    private final GamePlayerAnswerRepository gamePlayerAnswerRepository;

    @Override
    public List<GamePlayerDetailResponseDto> getTodayGameAnswers(String userId, LocalDate targetDate) {
        return gamePlayerAnswerRepository.findTodayGameAnswers(userId, targetDate);
    }

    @Override
    public int getCountByGameIdAndPlayerId(String gameId, String playerId){
        return gamePlayerAnswerRepository.countByIdGameIdAndIdPlayerId(gameId, playerId).orElse(0);
    }
}
