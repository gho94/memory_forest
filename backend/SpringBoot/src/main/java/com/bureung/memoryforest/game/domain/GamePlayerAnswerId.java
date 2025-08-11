package com.bureung.memoryforest.game.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.io.Serializable;

@Embeddable
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GamePlayerAnswerId implements Serializable {
    @Column(name = "game_id", length = 10)
    private String gameId;

    @Column(name = "game_seq")
    private Integer gameSeq;

    @Column(name = "player_id", length = 10)
    private String playerId;
}