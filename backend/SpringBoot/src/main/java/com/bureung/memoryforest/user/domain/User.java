package com.bureung.memoryforest.user.domain;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.List;

@Entity
@Table(name = "USERS")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User implements UserDetails{ //UserDetail이라는 인터페이스를 스프링 시큐리티에서 제공하는거라고 하네용 ~
    @Id
    @Column(name = "USER_ID", length = 10, nullable = false)
    private String userId;
    
    @Column(name = "LOGIN_ID", nullable = false, length = 100, unique = true)
    private String loginId;
    
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

    @Builder.Default    //null - default으로 해주기 위해서 필요한거임
    @Column(name = "LOGIN_TYPE",length = 20,nullable=false)
    private String loginType  ="DEFULAT";

    @Column(name = "SOCIAL_ID",length = 100)
    private String socialId;

    // UserDetails 인터페이스 구현하는 부분임다.
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        // userTypeCode를 기반으로 권한 설정
        return List.of(new SimpleGrantedAuthority("ROLE_" + userTypeCode)); //시큐리티 규칙이라고 함.. 권한은 ROLE_
    }

    @Override
    public String getUsername() {
        return this.loginId; // loginId를 username으로 - 시큐리티는 로그인시 입력하는 id값을 username으로 인식하는 규칙..
    }

    @Override
    public String getPassword() {
        return this.password;
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    // A20005 - 활성, A20006  - 비활성 , A20007  - 정지 , A20008  - 삭제 (공통코드 발췌 )
    @Override
    public boolean isAccountNonLocked() {
        // STATUS_CODE가 "A20005"(활성)인 경우만 잠김 해제
        return "A20005".equals(this.statusCode);
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        // STATUS_CODE가 "A20005"(활성)인 경우만 활성화
        return "A20005".equals(this.statusCode);
    }

    public String getUserName() {
        return this.userName;
    }

    public String getLoginType() {
        return this.loginType;
    }
}