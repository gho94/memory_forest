package com.bureung.memoryforest.record.controller;

import com.bureung.memoryforest.record.application.RecordService;
import com.bureung.memoryforest.record.dto.request.RecordCreateRequestDto;
import com.bureung.memoryforest.record.dto.response.RecordListResponseDto;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;  // 추가
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/recorder/record")
public class RecorderRecordController {

    private final RecordService recordService;

    @PostMapping("/create")
    public ResponseEntity<String> createRecord(
            @RequestBody RecordCreateRequestDto request, // JSON으로 받기
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

    @GetMapping("/list")
    public ResponseEntity<List<RecordListResponseDto>> getRecords(
            @RequestParam("year") int year,
            @RequestParam("month") int month,
            HttpServletRequest httpRequest) {

        try {
            HttpSession session = httpRequest.getSession();
            String userId = (String) session.getAttribute("user_id");
            userId = "U0002";  // TODO : leb. I'll change user id of session
            log.info("기록 리스트 조회 요청 - 사용자: {}, 년도: {}, 월: {}", userId, year, month);

            List<RecordListResponseDto> records = recordService.getRecordsByYearMonth(userId, year, month);

            return ResponseEntity.ok(records);

        } catch (Exception e) {
            log.error("기록 조회 중 오류 발생", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @GetMapping("/today-exists")
    public ResponseEntity<Map<String, Boolean>> checkTodayRecord(HttpServletRequest httpRequest) {
        try {
            HttpSession session = httpRequest.getSession();
            String userId = (String) session.getAttribute("user_id");
            userId = "U0002";  // TODO : leb. I'll change user id of session

            boolean exists = recordService.hasRecordToday(userId);

            Map<String, Boolean> response = Map.of("exists", exists);
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            log.error("오늘 기록 확인 중 오류 발생", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}
