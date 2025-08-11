package com.bureung.memoryforest.user.dto.request;

import lombok.Data;

@Data
public class RecorderCreateDto {
    private String userId;
    private String loginId;
    private String userName;
    private String birthDate;
    private String relationshipCode;
    private String genderCode;
    private String userTypeCode;
}
