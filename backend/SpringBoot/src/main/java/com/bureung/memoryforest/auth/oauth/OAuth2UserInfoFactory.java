package com.bureung.memoryforest.auth.oauth;

import java.util.Map;

// 팩토리 클래스 - 플랫폼별로 적절한 UserInfo 객체 생성
public class OAuth2UserInfoFactory {
    public static OAuth2UserInfo getOAuth2UserInfo(String registrationId, Map<String, Object> attributes) {
        switch (registrationId.toLowerCase()) {
            case "naver":
                return new NaverOAuth2UserInfo(attributes);
            case "kakao":
                return new KakaoOAuth2UserInfo(attributes);
            default:
                throw new IllegalArgumentException("지원하지 않는 소셜 로그인입니다: " + registrationId);
        }
    }
}
