package com.bureung.memoryforest.record.application.impl;

import com.bureung.memoryforest.common.application.FileService;
import com.bureung.memoryforest.common.domain.FileInfo;
import com.bureung.memoryforest.record.application.RecordService;
import com.bureung.memoryforest.record.repository.RecordRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import com.bureung.memoryforest.record.domain.Record;

@Service
public class RecordServiceImpl implements RecordService {
    @Autowired
    private FileService fileService;  // FileService 주입받아서 사용
    @Autowired
    private RecordRepository recordRepository;

    public void saveRecord(MultipartFile file, String text, Integer duration, String userId) {
        // 1. 파일 S3 업로드
        FileInfo uploadedFile = fileService.uploadFileToS3(file);

        // 2. DB 저장
        Record record = Record.builder()
                .userId(userId)
                .fileId(uploadedFile.getFileId())
                .text(text)
                .duration(duration) // 녹음 시간 저장
                .build();

        recordRepository.save(record);
    }
}
