package com.bureung.memoryforest.auth.application;

import com.bureung.memoryforest.auth.oauth.CustomOAuth2User;
import com.bureung.memoryforest.auth.oauth.OAuth2UserInfo;
import com.bureung.memoryforest.auth.oauth.OAuth2UserInfoFactory;
import com.bureung.memoryforest.user.application.UserService;
import com.bureung.memoryforest.user.domain.User;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.Optional;


@Slf4j
@Service
@RequiredArgsConstructor
public class CustomOAuth2UserService extends DefaultOAuth2UserService {

    private final UserService userService;

    @Override
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {
        OAuth2User oAuth2User = super.loadUser(userRequest);

        // 어떤 소셜 로그인인지 확인 (naver, kakao 등)
        String registrationId = userRequest.getClientRegistration().getRegistrationId();

        // OAuth2 사용자 정보 추출
        Map<String, Object> attributes = oAuth2User.getAttributes();

        log.info("OAuth2 로그인 시도 - Provider: {}, Attributes: {}", registrationId, attributes);

        // 프로바이더별로 사용자 정보 처리
        User user = processOAuth2User(registrationId, attributes);

        // 커스텀 OAuth2User 객체 반환
        return new CustomOAuth2User(user, attributes, getUserNameAttributeName(registrationId));
    }

    private User processOAuth2User(String registrationId, Map<String, Object> attributes) {
        OAuth2UserInfo userInfo = OAuth2UserInfoFactory.getOAuth2UserInfo(registrationId, attributes);

        if (userInfo.getEmail() == null || userInfo.getEmail().isEmpty()) {
            throw new OAuth2AuthenticationException("이메일 정보를 찾을 수 없습니다.");
        }

        String loginType = getLoginType(registrationId);

        // 소셜 ID로 기존 사용자 찾기
        Optional<User> existingUser = userService.findByLoginTypeAndSocialId(loginType, userInfo.getId());

        if (existingUser.isPresent()) {
            // 기존 사용자 정보 업데이트
            return userService.updateOAuthUser(
                    existingUser.get(),
                    userInfo.getName(),
                    userInfo.getEmail(),
                    userInfo.getPhone()
            );
        } else {
            // 이메일로 기존 사용자 확인 (일반 로그인 사용자가 OAuth로 로그인하는 경우)
            Optional<User> userByEmail = userService.findByEmail(userInfo.getEmail());
            if (userByEmail.isPresent()) {
                throw new OAuth2AuthenticationException("이미 해당 이메일로 가입된 계정이 있습니다.");
            }
            // 새 사용자 등록
            return userService.createOAuthUser(
                    userInfo.getName(),
                    userInfo.getEmail(),
                    userInfo.getPhone(),
                    loginType,
                    userInfo.getId(),
                    "A20002"
            );
        }
    }

    private String getLoginType(String registrationId) {
        switch (registrationId.toLowerCase()) {
            case "naver":
                return "NAVER";
            case "kakao":
                return "KAKAO";
            default:
                return "DEFAULT";
        }
    }

    private String getUserNameAttributeName(String registrationId) {
        switch (registrationId.toLowerCase()) {
            case "naver":
                return "response";
            case "kakao":
                return "id";
            default:
                return "id";
        }
    }

}
