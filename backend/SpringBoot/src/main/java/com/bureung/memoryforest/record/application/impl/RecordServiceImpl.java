package com.bureung.memoryforest.record.application.impl;

import com.bureung.memoryforest.record.application.RecordService;
import com.bureung.memoryforest.record.dto.response.RecordListResponseDto;
import com.bureung.memoryforest.record.repository.RecordRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import com.bureung.memoryforest.record.domain.Record;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class RecordServiceImpl implements RecordService {
    private final RecordRepository recordRepository;

    @Override
    @Transactional
    public void saveRecord(Integer fileId, String text, Integer duration, String userId) {
        log.info("레코드 저장 시작: fileId={}, userId={}, duration={}", fileId, userId, duration);

        try {
            Record record = Record.builder()
                    .userId(userId)
                    .fileId(fileId)
                    .text(text)
                    .duration(duration)
                    .build();

            Record savedRecord = recordRepository.save(record);
            log.info("레코드 저장 완료: recordId={}", savedRecord.getRecordId());

        } catch (Exception e) {
            log.error("레코드 저장 실패: fileId={}, userId={}", fileId, userId, e);
            throw new RuntimeException("레코드 저장에 실패했습니다.", e);
        }
    }

    @Override
    public List<RecordListResponseDto> getRecordsByYearMonth(String userId, int year, int month) {
        // 해당 년도/월의 시작일과 마지막일 계산
        LocalDateTime startDate = LocalDate.of(year, month, 1).atStartOfDay();
        LocalDateTime endDate = startDate.withDayOfMonth(startDate.toLocalDate().lengthOfMonth());

        log.info("기록 조회 - 사용자: {}, 기간: {} ~ {}", userId, startDate, endDate);

        List<Record> records = recordRepository.findByUserIdAndCreatedAtBetweenOrderByCreatedAtDesc(
                userId, startDate, endDate);

        return records.stream()
                .map(this::convertToListDto)
                .collect(Collectors.toList());
    }

    @Override
    public boolean hasRecordToday(String userId) {
        LocalDate today = LocalDate.now(ZoneId.of("Asia/Seoul"));
        return recordRepository.existsByUserIdAndCreatedAt(userId, today) > 0;
    }

    private RecordListResponseDto convertToListDto(Record record) {
        return RecordListResponseDto.builder()
                .recordId(record.getRecordId())
                .fileId(record.getFileId())
                .text(record.getText())
                .duration(record.getDuration())
                .createdAt(record.getCreatedAt())
                .build();
    }
}
