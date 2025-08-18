package com.bureung.memoryforest.user.controller;

import java.util.List;
import java.util.Optional;

import com.bureung.memoryforest.user.dto.request.RecorderCreateDto;
import com.bureung.memoryforest.user.dto.request.RecorderUpdateDto;
import com.bureung.memoryforest.user.dto.response.RecorderListResponseDto;
import lombok.extern.slf4j.Slf4j;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.bureung.memoryforest.user.application.UserService;
import com.bureung.memoryforest.user.domain.User;

import lombok.RequiredArgsConstructor;

@Slf4j
@RequiredArgsConstructor
@RestController
@RequestMapping("/companion/user")
public class CompanionUserController {

    private final UserService userService;

    @GetMapping("/mypage")
    public ResponseEntity<User> getCompanionMypage(@RequestParam String userId) {
        Optional<User> user = userService.findByUserId(userId);
        if (user.isPresent()) {
            return ResponseEntity.ok(user.get());
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping("/create")
    public ResponseEntity<User> createRecorderUser(@RequestBody RecorderCreateDto requestDto) {
        try {
            User user = userService.createRecorderUser(requestDto);
            return ResponseEntity.ok(user);
        } catch (Exception e) {
            log.error("기록자 생성 실패", e);
            return ResponseEntity.badRequest().build();
        }
    }

    @PostMapping("/update")
    public ResponseEntity<User> updateRecorderUser(@RequestBody RecorderUpdateDto requestDto) {
        try {
            User user = userService.updateRecorderUser(requestDto);
            return ResponseEntity.ok(user);
        } catch (Exception e) {
            log.error("기록자 수정 실패", e);
            return ResponseEntity.badRequest().build();
        }
    }

    @GetMapping("/list")
    public ResponseEntity<List<RecorderListResponseDto>> getRecorderList(@RequestParam String userId) {
        List<RecorderListResponseDto> recorderList = userService.getRecorderList(userId);
        return ResponseEntity.ok(recorderList);
    }
}
