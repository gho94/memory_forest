package com.bureung.memoryforest.auth.controller;

import com.bureung.memoryforest.auth.application.PatientShareService;
import com.bureung.memoryforest.auth.application.RefreshTokenService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletResponse;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/recorder")
@RequiredArgsConstructor
public class PatientShareController {

    private final PatientShareService patientShareService;
    private final RefreshTokenService refreshTokenService;

    /**
     * 환자 공유 링크 생성 (가족이 사용)
     */
    @PostMapping("/{patientId}/share")
    public ResponseEntity<Map<String, Object>> createShareLink(@PathVariable String patientId) {
        Map<String, Object> response = new HashMap<>();

        try {
            String shareUrl = patientShareService.generateShareLink(patientId);

            response.put("success", true);
            response.put("shareUrl", shareUrl);
            response.put("message", "공유 링크가 생성되었습니다.");

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            log.error("공유 링크 생성 실패 - 환자ID: {}, 오류: {}", patientId, e.getMessage());

            response.put("success", false);
            response.put("message", "공유 링크 생성에 실패했습니다.");

            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 공유 링크로 환자 로그인 (15분 Access + 2주 Refresh 토큰 발급)
     * 프론트엔드에서 환자 ID와 이름을 받아서 기존 대시보드로 이동
     */
    @PostMapping("/login/{accessCode}")
    public ResponseEntity<Map<String, Object>> loginWithShareLink(
            @PathVariable String accessCode,
            HttpServletResponse httpResponse) {

        try {
            Map<String, Object> loginResult = patientShareService.loginWithAccessCode(accessCode);

            if (loginResult != null && (Boolean) loginResult.get("success")) {
                // Refresh Token을 HttpOnly 쿠키에 저장 (보안강화)
                String refreshToken = (String) loginResult.get("refreshToken");
                Cookie refreshCookie = new Cookie("REFRESH_TOKEN", refreshToken);
                refreshCookie.setHttpOnly(true);
                refreshCookie.setSecure(false); // 개발환경에서는 false, 운영에서는 true
                refreshCookie.setPath("/");
                refreshCookie.setMaxAge(14 * 24 * 60 * 60); // 2주 (초단위)
                httpResponse.addCookie(refreshCookie);

                // 응답에서 refreshToken 제거 (쿠키로만 관리)
                loginResult.remove("refreshToken");

                log.info("환자 로그인 성공 - 접근코드: {}, 환자ID: {}", accessCode, loginResult.get("patientId"));
                return ResponseEntity.ok(loginResult);
            } else {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("success", false);
                errorResponse.put("message", "유효하지 않거나 만료된 링크입니다.");

                return ResponseEntity.badRequest().body(errorResponse);
            }

        } catch (Exception e) {
            log.error("환자 로그인 실패 - 접근코드: {}", accessCode, e);

            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("message", "로그인 처리 중 오류가 발생했습니다.");

            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    /**
     * Refresh Token으로 Access Token 갱신
     */
    @PostMapping("/refresh")
    public ResponseEntity<Map<String, Object>> refreshAccessToken(
            @CookieValue(name = "REFRESH_TOKEN", required = false) String refreshToken) {

        Map<String, Object> response = new HashMap<>();

        try {
            if (refreshToken == null) {
                response.put("success", false);
                response.put("message", "Refresh Token이 없습니다.");
                return ResponseEntity.badRequest().body(response);
            }

            String newAccessToken = refreshTokenService.generateNewAccessToken(refreshToken);

            response.put("success", true);
            response.put("accessToken", newAccessToken);
            response.put("message", "토큰이 갱신되었습니다.");

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            log.error("토큰 갱신 실패", e);

            response.put("success", false);
            response.put("message", "토큰 갱신에 실패했습니다. 다시 로그인해주세요.");

            return ResponseEntity.badRequest().body(response);
        }
    }

    /**
     * 로그아웃 (토큰 삭제)
     */
    @PostMapping("/logout")
    public ResponseEntity<Map<String, Object>> logout(
            @CookieValue(name = "REFRESH_TOKEN", required = false) String refreshToken,
            HttpServletResponse httpResponse) {

        Map<String, Object> response = new HashMap<>();

        try {
            if (refreshToken != null) {
                refreshTokenService.deleteRefreshToken(refreshToken);
            }

            // 쿠키 삭제
            Cookie refreshCookie = new Cookie("REFRESH_TOKEN", null);
            refreshCookie.setMaxAge(0);
            refreshCookie.setPath("/");
            httpResponse.addCookie(refreshCookie);

            response.put("success", true);
            response.put("message", "로그아웃되었습니다.");

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            log.error("로그아웃 실패", e);

            response.put("success", false);
            response.put("message", "로그아웃 처리 중 오류가 발생했습니다.");

            return ResponseEntity.badRequest().body(response);
        }
    }
}