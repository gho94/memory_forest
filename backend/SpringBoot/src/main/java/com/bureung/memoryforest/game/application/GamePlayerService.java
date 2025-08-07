package com.bureung.memoryforest.game.application;

import com.bureung.memoryforest.game.domain.GamePlayer;

import java.util.Optional;

//leb. Recorder가 게임을 실제 플레이할 때 처리하는 로직 (퀴즈 응답, 채점 등)
public interface GamePlayerService {
    Optional<GamePlayer> getGamesByGameIdAndPlayerId(String gameId, String playerId);
}
