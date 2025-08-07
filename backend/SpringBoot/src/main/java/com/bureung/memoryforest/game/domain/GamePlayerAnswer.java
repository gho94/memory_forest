package com.bureung.memoryforest.game.domain;

import jakarta.persistence.Column;
import jakarta.persistence.EmbeddedId;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.time.LocalDateTime;

@Entity
@Table(name = "game_player_answer")
@Getter
@Setter
@NoArgsConstructor
public class GamePlayerAnswer {

    @EmbeddedId
    private GamePlayerAnswerId id;

    @Column(name = "selected_option", nullable = false)
    private Integer selectedOption;

    @Column(name = "is_correct", length = 1, nullable = false)
    private String isCorrect;

    @Column(name = "answer_time_ms")
    private Integer answerTimeMs;

    @Column(name = "score_earned")
    private Integer scoreEarned;

    @Column(name = "answered_at")
    private LocalDateTime answeredAt;

    // 편의 메서드들
    public String getGameId() {
        return id != null ? id.getGameId() : null;
    }

    public Integer getGameSeq() {
        return id != null ? id.getGameSeq() : null;
    }

    public String getPlayerId() {
        return id != null ? id.getPlayerId() : null;
    }

    public boolean isCorrect() {
        return "Y".equals(this.isCorrect);
    }
}