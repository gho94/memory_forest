package com.bureung.memoryforest.game.application;

import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.game.repository.GameMasterRepository;

import java.util.List;

public class GameMasterService {
    private final GameMasterRepository gameMasterRepository;

    public GameMasterService(GameMasterRepository gameMasterRepository) {
        this.gameMasterRepository = gameMasterRepository;
    }

    public List<GameMaster> getGamesByGameName(String gameName) {
        return gameMasterRepository.findByGameName(gameName);
    }

    public GameMaster saveGame(GameMaster game) {
        return gameMasterRepository.save(game);
    }
}
