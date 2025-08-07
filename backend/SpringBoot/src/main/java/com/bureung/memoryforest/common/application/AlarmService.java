package com.bureung.memoryforest.common.application;
import com.bureung.memoryforest.common.dto.response.AlarmResponseDto;

import java.util.List;

public interface AlarmService {

    void sendGameCompletionAlarm(String gameId);

    List<AlarmResponseDto> getAllAlarms(String userId, int page, int size);

    void markAsRead(int alarmId, String userId);

}