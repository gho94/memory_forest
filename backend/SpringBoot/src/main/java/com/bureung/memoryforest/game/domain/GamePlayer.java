package com.bureung.memoryforest.game.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "game_player")
@Getter
@Setter
@NoArgsConstructor
public class GamePlayer {

    @EmbeddedId
    private GamePlayerId id;

    @Column(name = "total_score")
    private Integer totalScore;

    @Column(name = "correct_count")
    private Integer correctCount;

    @Column(name = "accuracy_rate", precision = 5, scale = 2)
    private BigDecimal accuracyRate;

    @Column(name = "game_status_code", length = 6, nullable = false)
    private String gameStatusCode;

    @Column(name = "start_time")
    private LocalDateTime startTime;

    @Column(name = "end_time")
    private LocalDateTime endTime;

    @Column(name = "duration_seconds")
    private Integer durationSeconds;
}
