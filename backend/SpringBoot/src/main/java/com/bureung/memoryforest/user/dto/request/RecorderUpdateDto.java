package com.bureung.memoryforest.user.dto.request;

import lombok.Data;

@Data
public class RecorderUpdateDto {
    private String userId;
    private String userName;
    private String loginId;
    private String password;
    private String email;
    private String phone;
    private String birthDate;
    private String genderCode;
    private String statusCode;
}
