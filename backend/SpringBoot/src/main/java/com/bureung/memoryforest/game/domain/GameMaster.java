package com.bureung.memoryforest.game.domain;

import lombok.*;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "GAME_MASTER")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@ToString
public class GameMaster {

    @Id
    @Column(name = "GAME_ID", length = 10)
    private String gameId;

    @Column(name = "GAME_NAME", length = 100, nullable = false)
    private String gameName;

    @Column(name = "GAME_DESC", length = 200)
    private String gameDesc;

    @Column(name = "GAME_COUNT", nullable = false)
    private Integer gameCount;

    @Column(name = "DIFFICULTY_LEVEL_CODE", nullable = false, length = 6)
    private String difficultyLevel;

    @Column(name = "CREATION_STATUS_CODE", length = 6, nullable = false)
    private String creationStatusCode; // CREATING/COMPLETED/PUBLISHED/INACTIVE

    @Column(name = "CREATED_BY", length = 5, nullable = false)
    private String createdBy;

    @Column(name = "CREATED_AT")
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "UPDATED_BY", length = 5)
    private String updatedBy;

    @Column(name = "UPDATED_AT")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void prePersist() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
        if (creationStatusCode == null) {
            creationStatusCode = "CREATING";
        }
    }

    @PreUpdate
    protected void preUpdate() {
        updatedAt = LocalDateTime.now();
    }
}