package com.bureung.memoryforest.common.controller;

import com.bureung.memoryforest.common.application.AlarmService;
import com.bureung.memoryforest.common.dto.response.AlarmResponseDto;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/alarms")
@RequiredArgsConstructor
public class AlarmController {

    private final AlarmService alarmService;

    // 대시보드에서 모든 알람 조회
    @GetMapping
    public ResponseEntity<List<AlarmResponseDto>> getAllAlarms(HttpSession session) {
//        String userId = (String) session.getAttribute("userId");
        String userId = "U0001";
        List<AlarmResponseDto> alarms = alarmService.getAllAlarms(userId, 1, 10);
        return ResponseEntity.ok(alarms);
    }

    // 알람 읽음 처리
    @PutMapping("/{alarmId}/read")
    public ResponseEntity<Void> markAsRead(@PathVariable Integer alarmId, HttpSession session) {
//        String userId = (String) session.getAttribute("userId");
        String userId = "U0001";
        alarmService.markAsRead(alarmId, userId);
        return ResponseEntity.ok().build();
    }
}