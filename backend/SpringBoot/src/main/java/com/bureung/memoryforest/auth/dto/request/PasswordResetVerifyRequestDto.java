package com.bureung.memoryforest.auth.dto.request;

import lombok.Data;

@Data
public class PasswordResetVerifyRequestDto {
    private String loginId;
    private String email;
    private String code;
}
