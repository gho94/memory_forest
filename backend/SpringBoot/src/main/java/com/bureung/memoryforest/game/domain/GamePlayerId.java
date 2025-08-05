package com.bureung.memoryforest.game.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import java.io.Serializable;
import java.util.Objects;

@Embeddable
public class GamePlayerId implements Serializable {

    @Column(name = "GAME_ID", length = 10)
    private String gameId;

    @Column(name = "PLAYER_ID", length = 10)
    private String playerId;

    public GamePlayerId() {}

    public GamePlayerId(String gameId, String playerId) {
        this.gameId = gameId;
        this.playerId = playerId;
    }

    // equals & hashCode 필수
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof GamePlayerId)) return false;
        GamePlayerId that = (GamePlayerId) o;
        return Objects.equals(gameId, that.gameId) &&
                Objects.equals(playerId, that.playerId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(gameId, playerId);
    }
}
