package com.bureung.memoryforest.game.application.impl;

import com.bureung.memoryforest.game.application.GameDetailService;
import com.bureung.memoryforest.game.application.GamePlayerAnswerService;
import com.bureung.memoryforest.game.domain.GamePlayerAnswer;
import com.bureung.memoryforest.game.domain.GamePlayerAnswerId;
import com.bureung.memoryforest.game.dto.request.CreateGamePlayerAnswerRequestDto;
import com.bureung.memoryforest.game.dto.response.GamePlayResultResponseDto;
import com.bureung.memoryforest.game.dto.response.GamePlayerDetailResponseDto;
import com.bureung.memoryforest.game.repository.GamePlayerAnswerRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class GamePlayerAnswerServiceImpl implements GamePlayerAnswerService {

    private final GamePlayerAnswerRepository gamePlayerAnswerRepository;
    private final GameDetailService gameDetailService;

    @Override
    public List<GamePlayerDetailResponseDto> getTodayGameAnswers(String userId, LocalDate targetDate) {
        return gamePlayerAnswerRepository.findTodayGameAnswers(userId, targetDate);
    }

    @Override
    public int getCountByGameIdAndPlayerId(String gameId, String playerId){
        return gamePlayerAnswerRepository.countByIdGameIdAndIdPlayerId(gameId, playerId).orElse(0);
    }

    @Override
    public int getMaxGameSeqByGameIdAndPlayerId (String gameId, String playerId){
        return gamePlayerAnswerRepository.findMaxGameSeqByGameIdAndPlayerId(gameId, playerId).orElse(0);
    }

    @Override
    public Integer createGamePlayerAnswer(CreateGamePlayerAnswerRequestDto request, String playerId){
        int score = 100;
        if (request.getIsCorrect().charAt(0) != 'Y') {
            String columnName = "wrong_score_"+(request.getSelectedOption()-1);
            score = gameDetailService.getScoreByColumn(request.getGameId(), request.getGameSeq(), columnName);
        }
        gamePlayerAnswerRepository.save(
                GamePlayerAnswer.builder()
                    .id(GamePlayerAnswerId.builder()
                        .gameId(request.getGameId())
                        .gameSeq(request.getGameSeq())
                        .playerId(playerId).build())
                    .selectedOption(request.getSelectedOption())
                    .isCorrect(request.getIsCorrect())
                    .answerTimeMs(request.getAnswerTimeMs())
                    .scoreEarned(score)
                    .answeredAt(LocalDateTime.now(ZoneId.of("Asia/Seoul")))
                        .build()
        );

        return score;
    }

    @Override
    public Optional<GamePlayResultResponseDto> getGamePlayAnswerResultSummary(String gameId, String playerId){
        return gamePlayerAnswerRepository.getGamePlayAnswerResultSummary(gameId, playerId);
    }
}
