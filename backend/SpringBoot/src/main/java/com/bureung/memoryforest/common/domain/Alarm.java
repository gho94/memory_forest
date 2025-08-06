package com.bureung.memoryforest.common.domain;
import com.bureung.memoryforest.game.domain.GamePlayer;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "ALARMS")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Alarm {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ALARM_ID")
    private Integer alarmId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumns({
            @JoinColumn(name = "GAME_ID", referencedColumnName = "game_id", nullable = false),
            @JoinColumn(name = "PLAYER_ID", referencedColumnName = "player_id", nullable = false)
    })
    private GamePlayer game;

    @Builder.Default
    @Column(name = "IS_READ", nullable = false, length = 1)
    private String isRead = "N";

    @Column(name = "CREATED_AT")
    private LocalDateTime createdAt;

    public void markAsRead() {
        this.isRead = "Y";
    }
}
