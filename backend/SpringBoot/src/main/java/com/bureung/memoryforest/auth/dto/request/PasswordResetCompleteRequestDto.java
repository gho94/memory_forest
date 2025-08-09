package com.bureung.memoryforest.auth.dto.request;

import lombok.Data;

@Data
public class PasswordResetCompleteRequestDto {
    private String userId;
    private String email;
    private String code;
    private String newPassword;
    private String confirmPassword;
}
