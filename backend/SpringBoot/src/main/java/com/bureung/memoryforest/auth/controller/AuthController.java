package com.bureung.memoryforest.auth.controller;

import com.bureung.memoryforest.auth.dto.LoginRequestDto;
import com.bureung.memoryforest.auth.dto.JoinRequestDto;
import com.bureung.memoryforest.user.domain.User;
import com.bureung.memoryforest.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.*;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Date;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @PostMapping("/login")
    public String login(@RequestBody LoginRequestDto loginRequest) {
        try {
            Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                    loginRequest.getUserId(),
                    loginRequest.getPassword()
                )
            );

            return "로그인 성공";

        } catch (AuthenticationException e) {
            return "로그인 실패: " + e.getMessage();
        }
    }

    @PostMapping("/join")
    public String join(@RequestBody JoinRequestDto dto) {
        System.out.println("회원가입 요청 도착: " + dto.getUserId());

        User user = User.builder()
            .user_id(dto.getUserId())
            .password(passwordEncoder.encode(dto.getPassword()))
            .user_name(dto.getUserName())
            .email(dto.getEmail())
            .phone(dto.getPhone())
            .user_type(dto.getUserType())
            .status("ACTIVE")
            .created_at(new Date())
            .build();

        userRepository.save(user);
        return "회원가입 성공";
    }
}
