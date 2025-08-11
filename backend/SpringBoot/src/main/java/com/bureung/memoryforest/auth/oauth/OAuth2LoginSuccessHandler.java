package com.bureung.memoryforest.auth.oauth;

import com.bureung.memoryforest.user.application.UserService;
import com.bureung.memoryforest.user.domain.User;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;
import org.springframework.web.util.UriComponentsBuilder;

import java.io.IOException;

@Slf4j
@Component
@RequiredArgsConstructor
public class OAuth2LoginSuccessHandler extends SimpleUrlAuthenticationSuccessHandler {

    private final UserService userService;

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response,
                                        Authentication authentication) throws IOException, ServletException {

        CustomOAuth2User oAuth2User = (CustomOAuth2User) authentication.getPrincipal();
        User user = oAuth2User.getUser();

        log.info("OAuth 로그인 성공: {} ({}) - {}", user.getUserName(), user.getLoginType(), user.getUserId());

        // 로그인 시간 업데이트
        userService.updateLoginTime(user.getUserId());

        // 세션에 사용자 정보 저장
        HttpSession session = request.getSession();
        session.setAttribute("userId", user.getUserId());
        session.setAttribute("userName", user.getUserName());
        session.setAttribute("userTypeCode", user.getUserTypeCode());
        session.setAttribute("loginType", user.getLoginType());

        // 사용자 타입에 따라 리다이렉트 URL 결정
        String redirectUrl = determineRedirectUrl(user.getUserTypeCode());

        log.info("OAuth 로그인 완료, 리다이렉트: {}", redirectUrl);

        // 성공 정보와 함께 리다이렉트
        UriComponentsBuilder uriBuilder = UriComponentsBuilder.fromUriString(redirectUrl)
                .queryParam("loginSuccess", true)
                .queryParam("loginType", user.getLoginType())
                .queryParam("userName", user.getUserName());

        getRedirectStrategy().sendRedirect(request, response, uriBuilder.build().toUriString());
    }

    private String determineRedirectUrl(String userTypeCode) {
        switch (userTypeCode) {
            case "A20001": // 환자 (RECORDER)
                return "http://localhost:3000/recorder/dashboard";
            case "A20002": // 가족 (COMPANION)
                return "http://localhost:3000/companion/dashboard";
            default:
                return "http://localhost:3000/companion/dashboard"; // 기본값
        }
    }

}
