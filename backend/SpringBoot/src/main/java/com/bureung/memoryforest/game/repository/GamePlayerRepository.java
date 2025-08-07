package com.bureung.memoryforest.game.repository;

import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.game.domain.GamePlayer;
import com.bureung.memoryforest.game.domain.GamePlayerId;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface GamePlayerRepository extends JpaRepository<GamePlayer, GamePlayerId> {
    Optional<GamePlayer> findByIdGameIdAndIdPlayerId(String gameId, String playerId);
}
