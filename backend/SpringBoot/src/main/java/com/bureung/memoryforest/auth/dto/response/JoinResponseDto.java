package com.bureung.memoryforest.auth.dto.response;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor(staticName = "of")
public class JoinResponseDto {
    private final boolean success;
    private final String message;

    public static JoinResponseDto success(String message) {
        return JoinResponseDto.of(true, message);
    }

    public static JoinResponseDto failure(String message) {
        return JoinResponseDto.of(false, message);
    }
}
