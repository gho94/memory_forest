package com.bureung.memoryforest.auth.dto.response;

import com.bureung.memoryforest.user.domain.User;
import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor(staticName = "of")
public class LoginResponseDto {
    private final boolean success;
    private final String message;
    private final User user;

    public static LoginResponseDto success(User user) {
        return LoginResponseDto.of(true, "로그인 성공", user);
    }

    public static LoginResponseDto failure(String message) {
        return LoginResponseDto.of(false, message, null);
    }
}
