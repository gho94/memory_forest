package com.bureung.memoryforest.game.application;

import com.bureung.memoryforest.game.domain.GameMaster;

import java.util.List;

public interface GameMasterService {
    List<GameMaster> getGamesByGameName(String gameName);
    GameMaster saveGame(GameMaster game);
}