package com.bureung.memoryforest.auth.controller;

import com.bureung.memoryforest.auth.application.PatientShareService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.util.Map;

@Slf4j
@RequiredArgsConstructor
@Controller
public class PatientShareController {

    private final PatientShareService patientShareService;

    // 공유 링크 생성 API
    @PostMapping("/api/recorder/{patientId}/share")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> generateShareLink(
            @PathVariable Long patientId,
            HttpSession session) {

        try {
            // 현재 로그인한 사용자 확인
            String userId = (String) session.getAttribute("userId");
            if (userId == null) {
                return ResponseEntity.status(401).body(Map.of(
                        "success", false,
                        "message", "로그인이 필요합니다."
                ));
            }

            // 공유 링크 생성
            String shareUrl = patientShareService.generateShareLink(patientId);

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "shareUrl", shareUrl,
                    "message", "공유 링크가 생성되었습니다."
            ));

        } catch (Exception e) {
            log.error("공유 링크 생성 실패 - 환자ID: {}", patientId, e);
            return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "message", "공유 링크 생성에 실패했습니다."
            ));
        }
    }

    // 환자 접근 처리 (공유된 링크 클릭 시)
    @GetMapping("/patient-view/{accessCode}")
    public String patientView(@PathVariable String accessCode,
                              HttpServletResponse response,
                              Model model) {

        try {
            // 접근 코드로 JWT 토큰 발급
            String jwt = patientShareService.processPatientAccess(accessCode);

            if (jwt == null) {
                model.addAttribute("error", "링크가 만료되었거나 유효하지 않습니다.");
                return "error/expired";
            }

            // JWT를 쿠키에 저장
            Cookie cookie = new Cookie("patientToken", jwt);
            cookie.setHttpOnly(true);
            cookie.setMaxAge(24 * 60 * 60); // 24시간
            cookie.setPath("/");
            response.addCookie(cookie);

            model.addAttribute("message", "환자 페이지 접근 성공!");
            return "patient/profile";

        } catch (Exception e) {
            log.error("환자 페이지 접근 실패 - 접근코드: {}", accessCode, e);
            model.addAttribute("error", "페이지 접근에 실패했습니다.");
            return "error/expired";
        }
    }
}