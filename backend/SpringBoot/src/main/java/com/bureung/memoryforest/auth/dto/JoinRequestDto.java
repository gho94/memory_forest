package com.bureung.memoryforest.auth.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class JoinRequestDto {
    private String userId;
    private String password;
    private String userName;
    private String email;
    private String phone;
    private String userType;
}
