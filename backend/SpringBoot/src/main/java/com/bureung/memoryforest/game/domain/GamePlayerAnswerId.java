package com.bureung.memoryforest.game.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.io.Serializable;
import java.util.Objects;

@Embeddable
@Getter
@Setter
@NoArgsConstructor
public class GamePlayerAnswerId implements Serializable {

    @Column(name = "game_id", length = 10)
    private String gameId;

    @Column(name = "game_seq")
    private Integer gameSeq;

    @Column(name = "player_id", length = 10)
    private String playerId;

    public GamePlayerAnswerId(String gameId, Integer gameSeq, String playerId) {
        this.gameId = gameId;
        this.gameSeq = gameSeq;
        this.playerId = playerId;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof GamePlayerAnswerId)) return false;
        GamePlayerAnswerId that = (GamePlayerAnswerId) o;
        return Objects.equals(gameId, that.gameId) &&
                Objects.equals(gameSeq, that.gameSeq) &&
                Objects.equals(playerId, that.playerId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(gameId, gameSeq, playerId);
    }
}
