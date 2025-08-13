package com.bureung.memoryforest.game.dto.request;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class GameDetailDto {
    private String gameTitle;
    private String gameDesc;
    private Integer fileId;
    private String answerText;
}
