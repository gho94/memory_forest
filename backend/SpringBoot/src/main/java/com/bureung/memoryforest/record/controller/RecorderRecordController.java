package com.bureung.memoryforest.record.controller;

import com.bureung.memoryforest.record.application.RecordService;
import jakarta.servlet.http.HttpSession;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@Slf4j
@RestController
@RequestMapping("/recorder/record")
public class RecorderRecordController {

    private RecordService recordService;

    @PostMapping("/create")
    public ResponseEntity<String> createRecord(
            @RequestParam("file") MultipartFile file,
            @RequestParam("text") String text,
            @RequestParam("duration") Integer duration, // 녹음 시간 추가
            HttpSession session) {
        log.info("음성파일 생성 API 호출: {}", file);
        String userId = (String) session.getAttribute("userId");
        if (userId == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("로그인이 필요합니다.");
        }

        try {
            recordService.saveRecord(file, text, duration, userId);
            return ResponseEntity.ok("success");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("저장 중 오류가 발생했습니다.");
        }
    }
}
