package com.bureung.memoryforest.user.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserRecorderResponseDto {
    private String userName;
    private String genderCode;
    private String birthDate;

    private String companionName;
    private String companionPhone;
    private String relationshipCode;
}
