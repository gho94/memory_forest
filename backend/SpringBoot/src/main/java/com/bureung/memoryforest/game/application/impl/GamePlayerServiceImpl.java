package com.bureung.memoryforest.game.application.impl;

import com.bureung.memoryforest.game.application.GamePlayerService;
import com.bureung.memoryforest.game.domain.GamePlayer;
import com.bureung.memoryforest.game.repository.GamePlayerRepository;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class GamePlayerServiceImpl implements GamePlayerService {
    private final GamePlayerRepository gamePlayerRepository;

    public GamePlayerServiceImpl(GamePlayerRepository gamePlayerRepository) {
        this.gamePlayerRepository = gamePlayerRepository;
    }

    @Override
    public Optional<GamePlayer> getGamesByGameIdAndPlayerId(String gameId, String playerId) {
        return gamePlayerRepository.findByIdGameIdAndIdPlayerId(gameId, playerId);
    }
}
