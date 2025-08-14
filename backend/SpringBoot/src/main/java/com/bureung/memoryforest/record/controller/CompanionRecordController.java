package com.bureung.memoryforest.record.controller;

import com.bureung.memoryforest.record.application.RecordService;
import com.bureung.memoryforest.record.dto.request.RecordDashboardRequestDto;
import com.bureung.memoryforest.record.dto.response.RecordDashboardResponseDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/companion/record")
public class CompanionRecordController {
    private final RecordService recordService;

    @GetMapping("/dashboard")
    public ResponseEntity<RecordDashboardResponseDto> getDashboard(RecordDashboardRequestDto request) {
        RecordDashboardResponseDto response = recordService.getDashboardStats(request);
        return ResponseEntity.ok(response);
    }
}
