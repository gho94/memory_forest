package com.bureung.memoryforest.record.dto.request;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class RecordCreateRequestDto {
    private Integer fileId;
    private String text;
    private Integer duration;
}

