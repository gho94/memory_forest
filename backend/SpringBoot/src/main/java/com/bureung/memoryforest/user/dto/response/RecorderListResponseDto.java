package com.bureung.memoryforest.user.dto.response;

import com.bureung.memoryforest.user.domain.User;
import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RecorderListResponseDto {
    private String userId;
    private String loginId;
    private String userName;
    private String email;
    private String phone;
    private String birthDate;
    private String genderCode;
    private String userTypeCode;
    private String statusCode;
    private String relationshipCode;
    
    public static RecorderListResponseDto from(User user, String relationshipCode) {
        return RecorderListResponseDto.builder()
                .userId(user.getUserId())
                .loginId(user.getLoginId())
                .userName(user.getUserName())
                .email(user.getEmail())
                .phone(user.getPhone())
                .birthDate(user.getBirthDate() != null ? user.getBirthDate().toString() : null)
                .genderCode(user.getGenderCode())
                .userTypeCode(user.getUserTypeCode())
                .statusCode(user.getStatusCode())
                .relationshipCode(relationshipCode)
                .build();
    }
}
