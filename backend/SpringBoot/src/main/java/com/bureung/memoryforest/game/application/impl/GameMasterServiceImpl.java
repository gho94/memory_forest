package com.bureung.memoryforest.game.application.impl;


import com.bureung.memoryforest.game.application.GameMasterService;
import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.game.repository.GameMasterRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class GameMasterServiceImpl implements GameMasterService {

    private final GameMasterRepository gameMasterRepository;

    public GameMasterServiceImpl(GameMasterRepository gameMasterRepository) {
        this.gameMasterRepository = gameMasterRepository;
    }

    @Override
    public List<GameMaster> getGamesByGameName(String gameName) {
        return gameMasterRepository.findByGameNameContaining(gameName);
    }

    @Override
    public Optional<GameMaster> getGamesByGameId(String gameId) {
        return gameMasterRepository.findByGameId(gameId);
    }

    @Override
    public GameMaster saveGame(GameMaster game) {
        return gameMasterRepository.save(game);
    }
}