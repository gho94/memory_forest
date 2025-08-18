package com.bureung.memoryforest.user.controller;

import com.bureung.memoryforest.user.dto.response.UserRecorderResponseDto;
import jakarta.servlet.http.HttpSession;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bureung.memoryforest.user.application.UserService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@RequiredArgsConstructor
@RestController
@RequestMapping("/recorder/user")
public class RecorderUserController {

    private final UserService userService;

    @GetMapping("/mypage")
    public ResponseEntity<UserRecorderResponseDto> getRecorderInfo(HttpSession session) {
        String userId = (String) session.getAttribute("userId");
        UserRecorderResponseDto userInfo = userService.getRecorderInfo(userId);
        log.info("my page : {}", userId);
        log.info("my page : {}", userInfo);
        return ResponseEntity.ok(userInfo);
    }
}
