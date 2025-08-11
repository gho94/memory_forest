package com.bureung.memoryforest.auth.dto.request;

import lombok.Data;

@Data
public class FindIdWithVerificationRequestDto {
    private String email;
    private String code;
}
