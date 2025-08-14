package com.bureung.memoryforest.common.application;
import com.bureung.memoryforest.common.dto.response.AlarmResponseDto;
import com.bureung.memoryforest.game.domain.GamePlayer;

import java.util.List;

public interface AlarmService {

    void sendGameCompletionAlarm(GamePlayer gamePlayer);

    List<AlarmResponseDto> getAllAlarms(String userId, int page, int size);

    void markAsRead(int alarmId, String userId);

}