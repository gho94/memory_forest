package com.bureung.memoryforest.game.dto.request;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class GameCreateRequestDto {
    private String gameName;
    private String gameDesc;
    private Integer gameCount;
    private String difficultyLevel;  // EASY, NORMAL, HARD
    private String createdBy;        // 생성자 ID
}
