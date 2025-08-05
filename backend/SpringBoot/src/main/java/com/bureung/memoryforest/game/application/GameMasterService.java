package com.bureung.memoryforest.game.application;

import com.bureung.memoryforest.game.domain.GameMaster;

import java.util.List;
import java.util.Optional;

public interface GameMasterService {
    List<GameMaster> getGamesByGameName(String gameName);
    Optional<GameMaster> getGamesByGameId(String gameId);
    GameMaster saveGame(GameMaster game);
}