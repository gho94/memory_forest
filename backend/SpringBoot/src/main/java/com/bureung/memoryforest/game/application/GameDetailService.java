package com.bureung.memoryforest.game.application;

import com.bureung.memoryforest.game.domain.GameDetail;

import java.util.Optional;

public interface GameDetailService {
    Optional<GameDetail> getGameDetailByGameIdAndGameSeq(String gameId, Integer gameSeq);
    int getScoreByColumn(String gameId, int gameSeq, String columnName);
}
