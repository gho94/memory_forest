package com.bureung.memoryforest.game.dto.request;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.util.List;

@Getter
@Setter
@ToString
@NoArgsConstructor
@AllArgsConstructor
public class UpdateStatusRequestDto {
    // 단일 게임 상태 업데이트용
    private String statusCode;
    private String updatedBy;
    
    // 배치 게임 상태 업데이트용
    private List<String> gameIds;
    private String targetStatus;
    private String description;
}