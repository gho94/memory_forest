package com.bureung.memoryforest.auth.oauth;

import com.bureung.memoryforest.user.domain.User;
import lombok.Getter;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.oauth2.core.user.OAuth2User;

import java.util.Collection;
import java.util.Map;

@Getter
public class CustomOAuth2User implements OAuth2User {
    private User user;
    private Map<String, Object> attributes;
    private String nameAttributeKey;

    public CustomOAuth2User(User user, Map<String, Object> attributes, String nameAttributeKey) {
        this.user = user;
        this.attributes = attributes;
        this.nameAttributeKey = nameAttributeKey;
    }

    @Override
    public Map<String, Object> getAttributes() {
        return attributes;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return user.getAuthorities();
    }

    @Override
    public String getName() {
        return user.getUserId();
    }

    // 추가 메소드들
    public String getUserId() {
        return user.getUserId();
    }

    public String getUserName() {
        return user.getUserName();
    }

    public String getEmail() {
        return user.getEmail();
    }

    public String getUserTypeCode() {
        return user.getUserTypeCode();
    }

    public String getLoginType() {
        return user.getLoginType();
    }

}
