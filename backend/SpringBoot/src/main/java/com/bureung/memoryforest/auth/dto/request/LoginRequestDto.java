package com.bureung.memoryforest.auth.dto.request;

import lombok.Data;

@Data
public class LoginRequestDto {
    private String loginId;
    private String password;
}
