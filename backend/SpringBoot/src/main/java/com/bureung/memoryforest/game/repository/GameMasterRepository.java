package com.bureung.memoryforest.game.repository;

import com.bureung.memoryforest.game.domain.GameMaster;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface GameMasterRepository extends JpaRepository<GameMaster, String> {
    List<GameMaster> findByGameNameContaining(String gameName);
}
