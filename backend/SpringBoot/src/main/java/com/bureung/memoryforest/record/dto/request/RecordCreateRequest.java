package com.bureung.memoryforest.record.dto.request;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class RecordCreateRequest {
    private Integer fileId;
    private String text;
    private Integer duration;
}

