package com.bureung.memoryforest.game.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import com.bureung.memoryforest.game.domain.GameDetail2;
import com.bureung.memoryforest.game.domain.GameDetailId;
import org.springframework.stereotype.Repository;

@Repository
public interface GameDetail2Repository extends JpaRepository<GameDetail2, GameDetailId> {
    List<GameDetail2> findByGameId(String gameId);
}
