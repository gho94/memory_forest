package com.bureung.memoryforest.common.dto.response;

import lombok.*;

import java.time.LocalDateTime;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AlarmResponseDto {

    private Integer alarmId;
    private String gameId;
    private String isRead;
    private LocalDateTime createdAt;
    private Integer totalScore;
    private String message;
    private String userId;
    private String userName;

    // totalScore 없이 생성하는 생성자 (JPQL용)
    public AlarmResponseDto(Integer alarmId, String gameId, String isRead, LocalDateTime createdAt, Integer totalScore, String userId, String userName) {
        this.alarmId = alarmId;
        this.gameId = gameId;
        this.isRead = isRead;
        this.createdAt = createdAt;
        this.totalScore = totalScore;
        this.userId = userId;
        this.userName = userName;
    }
}