package com.bureung.memoryforest.user.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "USERS")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {
    @Id
    @Column(name = "USER_ID", length = 10, nullable = false)
    private String userId;
    
    @Column(name = "USER_NAME", nullable = false, length = 100)
    private String userName;
    
    @Column(name = "PASSWORD", nullable = false, length = 60)
    private String password;
    
    @Column(name = "EMAIL", nullable = false, length = 100)
    private String email;
    
    @Column(name = "PHONE", length = 20)
    private String phone;
    
    @Column(name = "USER_TYPE_CODE", nullable = false, length = 6)
    private String userTypeCode;
    
    @Column(name = "PROFILE_IMAGE_FILE_ID")
    private Integer profileImageFileId;
    
    @Column(name = "STATUS_CODE", nullable = false, length = 6)
    private String statusCode;
    
    @Column(name = "CREATED_BY", nullable = false, length = 10)
    private String createdBy;
    
    @Column(name = "CREATED_AT", nullable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "UPDATED_BY", length = 10)
    private String updatedBy;
    
    @Column(name = "UPDATED_AT")
    private LocalDateTime updatedAt;
    
    @Column(name = "LOGIN_AT")
    private LocalDateTime loginAt;
}