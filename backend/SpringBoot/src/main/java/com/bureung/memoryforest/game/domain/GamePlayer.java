package com.bureung.memoryforest.game.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "GAME_PLAYER")
@Getter
@Setter
@NoArgsConstructor
public class GamePlayer {

    @EmbeddedId
    private GamePlayerId id;

    @Column(name = "TOTAL_SCORE")
    private Integer totalScore;

    @Column(name = "CORRECT_COUNT")
    private Integer correctCount;

    @Column(name = "ACCURACY_RATE", precision = 5, scale = 2)
    private BigDecimal accuracyRate;

    @Column(name = "GAME_STATUS_CODE", length = 6, nullable = false)
    private String gameStatusCode;

    @Column(name = "START_TIME")
    private LocalDateTime startTime;

    @Column(name = "END_TIME")
    private LocalDateTime endTime;

    @Column(name = "DURATION_SECONDS")
    private Integer durationSeconds;
}
