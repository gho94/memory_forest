package com.bureung.memoryforest.record.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RecordListResponseDto {
    private Integer recordId;
    private Integer fileId;
    private String text;
    private Integer duration; // 초 단위
    private LocalDateTime createdAt;
}
