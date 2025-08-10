package com.bureung.memoryforest.auth.dto.request;

import lombok.Data;

@Data
public class EmailVerifyRequestDto {
    private String email;
    private String code;
}
