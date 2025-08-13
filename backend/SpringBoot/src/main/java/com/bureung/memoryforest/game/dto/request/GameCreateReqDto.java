package com.bureung.memoryforest.game.dto.request;

import lombok.Getter;
import lombok.Setter;
import java.util.List;

@Getter
@Setter
public class GameCreateReqDto {
    private String gameName;
    private String createdBy;
    private List<GameDetailDto> gameDetails;
    private Integer totalProblems;
    private List<String> selectedPatients;
}
