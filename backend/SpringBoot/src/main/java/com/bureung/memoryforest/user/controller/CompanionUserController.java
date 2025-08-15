package com.bureung.memoryforest.user.controller;

import java.util.Optional;

import lombok.extern.slf4j.Slf4j;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.bureung.memoryforest.user.application.UserService;
import com.bureung.memoryforest.user.domain.User;

import lombok.RequiredArgsConstructor;

@Slf4j
@RequiredArgsConstructor
@RestController
public class CompanionUserController {

    private final UserService userService;

    @GetMapping("/companion/mypage")
    public ResponseEntity<User> getCompanionMypage(@RequestParam String userId) {
        Optional<User> user = userService.findByUserId(userId);
        if (user.isPresent()) {
            return ResponseEntity.ok(user.get());
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
