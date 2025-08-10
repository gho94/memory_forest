package com.bureung.memoryforest.game.domain;
import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;


@Entity
@Table(name = "game_master")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@ToString
public class GameMaster {
    @Id
    @Column(name = "game_id", nullable = false, length = 10)
    private String gameId;

    @Column(name = "game_name", nullable = false, length = 100)
    private String gameName;

    @Column(name = "game_desc", nullable = true, length = 200)
    private String gameDesc;

    @Column(name = "game_count", nullable = false)
    private Integer gameCount;

    @Column(name = "difficulty_level_code", nullable = false, length = 6)
    private String difficultyLevelCode;

    @Column(name = "creation_status_code", nullable = false, length = 6)
    private String creationStatusCode;

    @Column(name = "created_by", nullable = false, length = 10)
    private String createdBy;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_by", nullable = true, length = 10)
    private String updatedBy;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = true)
    private LocalDateTime updatedAt;
}
