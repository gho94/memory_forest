package com.bureung.memoryforest.game.dto.request;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class UpdateStatusRequestDto {
    private String statusCode;
    private String updatedBy;
}
