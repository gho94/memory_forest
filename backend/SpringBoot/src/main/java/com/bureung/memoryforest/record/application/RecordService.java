package com.bureung.memoryforest.record.application;

import org.springframework.web.multipart.MultipartFile;

public interface RecordService {

    void saveRecord(MultipartFile file, String text, Integer duration, String userId);
}
