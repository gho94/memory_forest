package com.bureung.memoryforest.game.domain;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.time.LocalDateTime;

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
    @Column(name = "game_id", length = 10, nullable = false)
    private String gameId; // PK

    @Column(name = "game_name", length = 100, nullable = false)
    private String gameName;

    @Column(name = "game_desc", length = 200)
    private String gameDesc;

    @Column(name = "game_count", nullable = false)
    private Integer gameCount;

    @Column(name = "difficulty_level_code", length = 6, nullable = false)
    private String difficultyLevelCode; // FK → common_codes.code_id

    @Column(name = "creation_status_code", length = 6, nullable = false)
    private String creationStatusCode; // FK → common_codes.code_id

    @Column(name = "created_by", length = 10, nullable = false)
    private String createdBy; // FK → users.user_id (관리자 or 가족)

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_by", length = 10)
    private String updatedBy;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        if (this.creationStatusCode == null) {
            this.creationStatusCode = "CREATING"; // 또는 정의서에 맞는 기본 상태
        }
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
