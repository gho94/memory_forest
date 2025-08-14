package com.bureung.memoryforest.common.application.impl;

import com.bureung.memoryforest.common.application.AlarmService;
import com.bureung.memoryforest.common.domain.Alarm;
import com.bureung.memoryforest.common.dto.response.AlarmResponseDto;
import com.bureung.memoryforest.common.repository.AlarmRepository;
import com.bureung.memoryforest.game.application.GameMasterService;
import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.game.domain.GamePlayer;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class AlarmServiceImpl implements AlarmService {

    private final AlarmRepository alarmRepository;
    private final GameMasterService gameMasterService;

    @Override
    public void sendGameCompletionAlarm(GamePlayer gamePlayer) {
        String gameId = gamePlayer.getId().getGameId();
        log.info("게임 완료 알람 발송 시작 - gameId: {}", gameId);

        // 게임 정보 조회 (가족 정보 포함)
        GameMaster gameMaster = gameMasterService.getGamesByGameId(gameId)
                .orElseThrow(() -> new IllegalArgumentException("게임을 찾을 수 없습니다."));

        // 가족(created_by)에게 알람 발송
        Alarm alarm = Alarm.builder()
                .game(gamePlayer)
                .isRead("N")
                .createdAt(LocalDateTime.now(ZoneId.of("Asia/Seoul")))
                .build();

        alarmRepository.save(alarm);
        log.info("알람 발송 완료 - 가족 userId: {}, 점수: {}", gameMaster.getCreatedBy(), gamePlayer.getTotalScore());
    }

    @Override
    @Transactional(readOnly = true)
    public List<AlarmResponseDto> getAllAlarms(String userId, int page, int size) {
        List<AlarmResponseDto> alarms = alarmRepository.findAlarmsByFamilyUserId(userId);

        // 조회할 때 점수별로 메시지 생성해서 추가!
        return alarms.stream()
                .map(alarm -> {
                    String message = generateAlarmMessage(alarm.getTotalScore());
                    alarm.setMessage(message);  // 메시지 설정
                    return alarm;
                })
                .collect(Collectors.toList());
    }

    @Override
    public void markAsRead(int alarmId, String userId) {
        alarmRepository.markAsReadById(alarmId);
        log.info("알람 읽음 처리 완료 - alarmId: {}", alarmId);
    }

    private String generateAlarmMessage(Integer totalScore) {
        if (totalScore >= 60) {
            return "오늘의 게임을 완료하였습니다.\n지금 바로 결과를 확인해보세요.";
        } else {
            return "오늘의 게임이 완료되었습니다.\n점수가 낮습니다. 빠른 확인이 필요합니다.";
        }
    }

}