package com.bureung.memoryforest.game.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import lombok.*;

import java.io.Serializable;

@Embeddable
@Data
@NoArgsConstructor
@AllArgsConstructor
public class GamePlayerId implements Serializable {
    @Column(name = "game_id", length = 10)
    private String gameId;

    @Column(name = "player_id", length = 10)
    private String playerId;
}