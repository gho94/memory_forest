package com.bureung.memoryforest.record.application;

public interface RecordService {

    void saveRecord(Integer fileId, String text, Integer duration, String userId);
}
