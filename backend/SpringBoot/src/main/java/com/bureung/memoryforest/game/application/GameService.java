package com.bureung.memoryforest.game.application;

import java.util.List;

import com.bureung.memoryforest.game.domain.GameDetail2;
import com.bureung.memoryforest.game.domain.GameMaster2;
import com.bureung.memoryforest.game.dto.request.GameCreateReqDto;

public interface GameService {
    List<GameMaster2> getAllGame();
    List<GameDetail2> getGameDetail(String gameId);
    GameMaster2 createGame(GameCreateReqDto gameCreateReqDto);
}
