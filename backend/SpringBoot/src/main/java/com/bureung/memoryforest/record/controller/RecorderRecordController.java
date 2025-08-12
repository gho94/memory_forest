package com.bureung.memoryforest.record.controller;

import com.bureung.memoryforest.record.application.RecordService;
import com.bureung.memoryforest.record.dto.request.RecordCreateRequest;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;  // 추가
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/recorder/record")
public class RecorderRecordController {

    private final RecordService recordService;

    @PostMapping("/create")
    public ResponseEntity<String> createRecord(
            @RequestBody RecordCreateRequest request, // JSON으로 받기
            HttpSession session) {

        log.info("음성 레코드 생성 API 호출: fileId={}, text={}, duration={}",
                request.getFileId(), request.getText(), request.getDuration());

        String userId = (String) session.getAttribute("userId");
        if (userId == null) {
            userId= "U0002";  // TODO : leb. I'll change user id of session
//            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("로그인이 필요합니다.");
        }

        try {
            recordService.saveRecord(request.getFileId(), request.getText(), request.getDuration(), userId);
            return ResponseEntity.ok("success");
        } catch (Exception e) {
            log.error("레코드 저장 중 오류 발생", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("저장 중 오류가 발생했습니다.");
        }
    }
}
