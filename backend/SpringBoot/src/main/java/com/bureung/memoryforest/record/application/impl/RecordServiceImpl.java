package com.bureung.memoryforest.record.application.impl;

import com.bureung.memoryforest.record.application.RecordService;
import com.bureung.memoryforest.record.repository.RecordRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import com.bureung.memoryforest.record.domain.Record;

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
}
