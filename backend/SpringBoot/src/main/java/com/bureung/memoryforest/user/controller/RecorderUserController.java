package com.bureung.memoryforest.user.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bureung.memoryforest.user.application.UserService;
import com.bureung.memoryforest.user.domain.User;
import com.bureung.memoryforest.user.dto.request.RecorderCreateDto;
import com.bureung.memoryforest.user.dto.response.RecorderListResponseDto;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@RequiredArgsConstructor
@RestController
@RequestMapping("/api/recorder")
public class RecorderUserController {

    private final UserService userService;

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

    @GetMapping("/list")
    public ResponseEntity<List<RecorderListResponseDto>> getRecorderList(@RequestParam String userId) {
        List<RecorderListResponseDto> recorderList = userService.getRecorderList(userId);
        return ResponseEntity.ok(recorderList);
    }
}
