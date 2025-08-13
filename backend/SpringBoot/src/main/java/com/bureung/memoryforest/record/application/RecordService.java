package com.bureung.memoryforest.record.application;

import com.bureung.memoryforest.record.dto.response.RecordListResponseDto;

import java.time.LocalDateTime;
import java.util.List;

public interface RecordService {

    void saveRecord(Integer fileId, String text, Integer duration, String userId);
    List<RecordListResponseDto> getRecordsByYearMonth(String userId, int year, int month);
    boolean hasRecordToday(String userId);
}
