package com.bureung.memoryforest.game.application;

import java.util.List;

import com.bureung.memoryforest.game.domain.GameDetail;
import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.game.dto.request.GameCreateReqDto;
import com.bureung.memoryforest.game.dto.response.GameListResponseDto;

public interface GameService {
    List<GameMaster> getAllGame();
    List<GameDetail> getGameDetail(String gameId);
    GameMaster createGame(GameCreateReqDto gameCreateReqDto);    
    List<GameListResponseDto> getGameListInfo();
}
