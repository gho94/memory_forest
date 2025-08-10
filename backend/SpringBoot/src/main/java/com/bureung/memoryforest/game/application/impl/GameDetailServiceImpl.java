package com.bureung.memoryforest.game.application.impl;

import com.bureung.memoryforest.game.application.GameDetailService;
import com.bureung.memoryforest.game.domain.GameDetail;
import com.bureung.memoryforest.game.repository.GameDetailRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class GameDetailServiceImpl implements GameDetailService {
    private final GameDetailRepository gameDetailRepository;
    @Override
    public Optional<GameDetail> getGameDetailByGameIdAndGameSeq(String gameId, Integer gameSeq){
        return gameDetailRepository.findByGameIdAndGameSeq(gameId, gameSeq);
    }

    @Override
    public int getScoreByColumn(String gameId, int gameSeq, String columnName) {
        return gameDetailRepository.findScoreByColumn(gameId, gameSeq, columnName).orElse(0);
    }
}
