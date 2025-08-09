package com.bureung.memoryforest.game.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "game_detail2")
@IdClass(GameDetailId.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GameDetail2 {
    @Id
    @Column(name = "game_id", nullable = false, length = 10)
    private String gameId;

    @Id
    @Column(name = "game_seq", nullable = false)
    private Integer gameSeq;

    @Column(name = "game_order", nullable = false)
    private Integer gameOrder;

    @Column(name = "file_id", nullable = false)
    private Integer fileId;

    @Column(name = "answer_text", nullable = true, length = 20)
    private String answerText;

    @Column(name = "wrong_option_1", nullable = true, length = 20)
    private String wrongOption1;

    @Column(name = "wrong_option_2", nullable = true, length = 20)
    private String wrongOption2;

    @Column(name = "wrong_option_3", nullable = true, length = 20)
    private String wrongOption3;

    @Column(name = "wrong_score_1", nullable = true)
    private Integer wrongScore1;

    @Column(name = "wrong_score_2", nullable = true)
    private Integer wrongScore2;

    @Column(name = "wrong_score_3", nullable = true)
    private Integer wrongScore3;

    @Column(name = "ai_status_code", nullable = false, length = 6)
    private String aiStatusCode;

    @Column(name = "ai_processed_at", nullable = true)  
    private LocalDateTime aiProcessedAt;

    @Column(name = "description", nullable = true, length = 200)
    private String description;
}
