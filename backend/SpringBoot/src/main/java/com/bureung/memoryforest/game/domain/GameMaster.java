package com.bureung.memoryforest.game.domain;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "GAME_MASTER")
public class GameMaster {
    @Id
    @Column(name = "GAME_ID", length = 10)
    private String gameId;

    @Column(name = "GAME_NAME", nullable = false, length = 100)
    private String gameName;

    @Column(name = "GAME_DESC", length = 200)
    private String gameDesc;

    @Column(name = "GAME_COUNT", nullable = false)
    private int gameCount;

    @Column(name = "DIFFICULTY_LEVEL", nullable = false, length = 6)
    private String difficultyLevel;

    @Column(name = "CREATION_STATUS_CODE", nullable = false, length = 6)
    private String creationStatusCode;

    @Column(name = "CREATED_BY", nullable = false, length = 5)
    private String createdBy;

    @Column(name = "CREATED_AT", columnDefinition = "TIMESTAMP DEFAULT SYSTIMESTAMP")
    private LocalDateTime createdAt;

    @Column(name = "UPDATED_BY", length = 5)
    private String updatedBy;

    @Column(name = "UPDATED_AT")
    private LocalDateTime updatedAt;

    // 기본 생성자
    public GameMaster() {}
}
