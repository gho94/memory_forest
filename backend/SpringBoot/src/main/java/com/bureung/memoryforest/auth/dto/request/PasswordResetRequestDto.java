package com.bureung.memoryforest.auth.dto.request;

import lombok.Data;

@Data
public class PasswordResetRequestDto {
    private String userId;
    private String email;
}
