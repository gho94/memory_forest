package com.bureung.memoryforest.auth.dto.request;

import lombok.Data;

@Data
public class JoinRequestDto {
    private String loginId;
    private String userName;
    private String password;
    private String email;
    private String phone;
    private String userTypeCode;
}
