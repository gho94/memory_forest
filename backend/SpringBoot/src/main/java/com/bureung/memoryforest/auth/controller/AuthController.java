package com.bureung.memoryforest.auth.controller;

import com.bureung.memoryforest.auth.application.AuthService;
import com.bureung.memoryforest.auth.application.EmailService;
import com.bureung.memoryforest.auth.dto.request.*;
import com.bureung.memoryforest.auth.dto.response.LoginResponseDto;
import com.bureung.memoryforest.auth.dto.response.JoinResponseDto;
import com.bureung.memoryforest.auth.dto.request.FindIdWithVerificationRequestDto;
import com.bureung.memoryforest.user.domain.User;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpSession;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@Slf4j
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@CrossOrigin(originPatterns = "*",allowCredentials = "true")
public class AuthController {

    private final AuthService authService;
    private final EmailService emailService;

    //api 테스트용 --- 추후 지워야함!!!!!!!!!!!!!!!!
    @GetMapping("/test")
    public ResponseEntity<String> test() {
        return ResponseEntity.ok("API 작동 중!");
    }

    //로그인
    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody LoginRequestDto loginRequest, HttpSession session) {

        LoginResponseDto result = authService.login(loginRequest.getUserId(), loginRequest.getPassword());

        Map<String, Object> response = new HashMap<>();

        if (!result.isSuccess()) {
            response.put("success", false);
            response.put("message", result.getMessage());
            return ResponseEntity.badRequest().body(response);
        }

        User user = result.getUser();

        session.setAttribute("userId", user.getUserId());
        session.setAttribute("userTypeCode", user.getUserTypeCode());
        session.setAttribute("userName", user.getUserName());

        response.put("success", true);
        response.put("message", "로그인 성공");
        response.put("userId", user.getUserId());
        response.put("userName", user.getUserName());
        response.put("userTypeCode", user.getUserTypeCode());
        response.put("email", user.getEmail());

        return ResponseEntity.ok(response);
    }

    //회원가입

    // 1. 아이디 중복 체크
    @GetMapping("/check/userid/{userId}")
    public ResponseEntity<Map<String, Object>> checkUserIdDuplicate(@PathVariable String userId) {
        boolean exists = authService.findByUserId(userId).isPresent();

        Map<String, Object> response = new HashMap<>();
        response.put("exists", exists);
        response.put("message", exists ? "이미 사용중인 ID입니다." : "사용 가능한 ID입니다.");

        return ResponseEntity.ok(response);
    }

    // 2. 이메일 인증번호 발송 (회원가입용)
    @PostMapping("/email/send")
    public ResponseEntity<Map<String, Object>> sendVerificationCode(@RequestBody EmailRequestDto emailRequest) {
        log.info("회원가입용 이메일 인증번호 발송 요청: {}", emailRequest.getEmail());

        Map<String, Object> response = new HashMap<>();

        // 이미 가입된 이메일인지 확인
        boolean emailExists = authService.existsByEmail(emailRequest.getEmail());
        if (emailExists) {
            response.put("success", false);
            response.put("message", "이미 가입된 이메일입니다.");
            return ResponseEntity.badRequest().body(response);
        }

        boolean success = emailService.sendVerificationCode(emailRequest.getEmail());

        if (success) {
            response.put("success", true);
            response.put("message", "인증번호가 전송되었습니다.");
        } else {
            response.put("success", false);
            response.put("message", "인증번호 전송에 실패했습니다.");
        }

        return ResponseEntity.ok(response);
    }

    // 3. 이메일 인증번호 확인 (회원가입용)
    @PostMapping("/email/verify")
    public ResponseEntity<Map<String, Object>> verifyCode(@RequestBody EmailVerifyRequestDto verifyRequest) {
        log.info("이메일 인증번호 확인 요청 - 이메일: {}, 코드: {}", verifyRequest.getEmail(), verifyRequest.getCode());

        Map<String, Object> response = new HashMap<>();

        boolean isValid = emailService.verifyCode(verifyRequest.getEmail(), verifyRequest.getCode());

        if (isValid) {
            response.put("success", true);
            response.put("message", "인증이 완료되었습니다.");
        } else {
            response.put("success", false);
            response.put("message", "인증번호가 올바르지 않거나 만료되었습니다.");
        }

        return ResponseEntity.ok(response);
    }

    // 4. 회원가입 완료
    @PostMapping("/signup")
    public ResponseEntity<Map<String, Object>> signup(@RequestBody JoinRequestDto signupRequest) {
        log.info("회원가입 요청 - 이메일: {}, 아이디: {}", signupRequest.getEmail(), signupRequest.getUserId());

        Map<String, Object> response = new HashMap<>();

        // 비밀번호 강도 검증
        String passwordValidationMessage = validatePassword(signupRequest.getPassword());
        if (passwordValidationMessage != null) {
            response.put("success", false);
            response.put("message", passwordValidationMessage);
            return ResponseEntity.badRequest().body(response);
        }

        JoinResponseDto result = authService.signup(signupRequest);

        response.put("success", result.isSuccess());
        response.put("message", result.getMessage());

        if (result.isSuccess()) {
            return ResponseEntity.ok(response);
        } else {
            return ResponseEntity.badRequest().body(response);
        }
    }


    //아이디 찾기
    // 1. 아이디 찾기용 이메일 인증번호 발송
    @PostMapping("/findid/email/send")
    public ResponseEntity<Map<String, Object>> sendFindIdVerificationCode(@RequestBody EmailRequestDto emailRequest) {
        log.info("아이디 찾기 인증번호 발송 요청: {}", emailRequest.getEmail());

        Map<String, Object> response = new HashMap<>();

        // 먼저 해당 이메일로 가입된 계정이 있는지 확인
        Optional<User> userOptional = authService.findByEmail(emailRequest.getEmail());
        if (userOptional.isEmpty()) {
            response.put("success", false);
            response.put("message", "해당 이메일로 가입된 계정이 없습니다.");
            return ResponseEntity.badRequest().body(response);
        }

        boolean success = emailService.sendVerificationCode(emailRequest.getEmail());

        if (success) {
            response.put("success", true);
            response.put("message", "인증번호가 전송되었습니다.");
        } else {
            response.put("success", false);
            response.put("message", "인증번호 전송에 실패했습니다.");
        }

        return ResponseEntity.ok(response);
    }

    // 2. 아이디 찾기 (인증번호 확인 후)
    @PostMapping("/findid")
    public ResponseEntity<Map<String, Object>> findUserId(@RequestBody FindIdWithVerificationRequestDto findIdRequest) {
        log.info("아이디 찾기 요청: {}", findIdRequest.getEmail());

        Map<String, Object> response = new HashMap<>();

        // 1. 인증번호 확인
        boolean isValidCode = emailService.verifyCode(findIdRequest.getEmail(), findIdRequest.getCode());
        if (!isValidCode) {
            response.put("success", false);
            response.put("message", "인증번호가 올바르지 않거나 만료되었습니다.");
            return ResponseEntity.badRequest().body(response);
        }

        // 2. 이메일로 사용자 찾기
        Optional<User> userOptional = authService.findByEmail(findIdRequest.getEmail());
        if (userOptional.isEmpty()) {
            response.put("success", false);
            response.put("message", "해당 이메일로 가입된 계정이 없습니다.");
            return ResponseEntity.badRequest().body(response);
        }

        User user = userOptional.get();
        String maskedUserId = maskUserId(user.getUserId());

        response.put("success", true);
        response.put("message", "아이디를 찾았습니다.");
        response.put("userId", maskedUserId);
        response.put("fullUserId", user.getUserId()); // 프론트에서 필요시 사용

        log.info("아이디 찾기 성공: {} -> {}", findIdRequest.getEmail(), maskedUserId);
        return ResponseEntity.ok(response);
    }

    //비밀번호 찾기
    // 1. 비밀번호 재설정 인증번호 발송
    @PostMapping("/password/reset/send")
    public ResponseEntity<Map<String, Object>> sendPasswordResetCode(@RequestBody PasswordResetRequestDto resetRequest) {
        log.info("비밀번호 재설정 인증번호 발송 요청: {} / {}", resetRequest.getUserId(), resetRequest.getEmail());

        Map<String, Object> response = new HashMap<>();

        // 아이디와 이메일로 사용자 찾기
        Optional<User> userOptional = authService.findByUserIdAndEmail(
                resetRequest.getUserId(),
                resetRequest.getEmail()
        );

        if (userOptional.isEmpty()) {
            response.put("success", false);
            response.put("message", "입력하신 아이디와 이메일이 일치하지 않습니다.");
            return ResponseEntity.badRequest().body(response);
        }

        // 비밀번호 재설정용 인증번호 발송
        boolean success = emailService.sendPasswordResetCode(resetRequest.getEmail());

        if (success) {
            response.put("success", true);
            response.put("message", "비밀번호 재설정 인증번호를 전송했습니다.");
        } else {
            response.put("success", false);
            response.put("message", "인증번호 전송에 실패했습니다.");
        }

        return ResponseEntity.ok(response);
    }

    // 2. 비밀번호 재설정 완료
    @PostMapping("/password/reset/complete")
    public ResponseEntity<Map<String, Object>> completePasswordReset(@RequestBody PasswordResetCompleteRequestDto resetCompleteRequest) {
        log.info("비밀번호 재설정 완료 요청: {} / {}", resetCompleteRequest.getUserId(), resetCompleteRequest.getEmail());

        Map<String, Object> response = new HashMap<>();

        // 1. 비밀번호 확인 검증
        if (!resetCompleteRequest.getNewPassword().equals(resetCompleteRequest.getConfirmPassword())) {
            response.put("success", false);
            response.put("message", "새 비밀번호와 비밀번호 확인이 일치하지 않습니다.");
            return ResponseEntity.badRequest().body(response);
        }

        // 2. 비밀번호 강도 검증
        String passwordValidationMessage = validatePassword(resetCompleteRequest.getNewPassword());
        if (passwordValidationMessage != null) {
            response.put("success", false);
            response.put("message", passwordValidationMessage);
            return ResponseEntity.badRequest().body(response);
        }

        // 3. 사용자 존재 확인
        Optional<User> userOptional = authService.findByUserIdAndEmail(
                resetCompleteRequest.getUserId(),
                resetCompleteRequest.getEmail()
        );

        if (userOptional.isEmpty()) {
            response.put("success", false);
            response.put("message", "입력하신 아이디와 이메일이 일치하지 않습니다.");
            return ResponseEntity.badRequest().body(response);
        }

        // 4. 인증번호 확인
        boolean isValidCode = emailService.verifyCode(resetCompleteRequest.getEmail(), resetCompleteRequest.getCode());
        if (!isValidCode) {
            response.put("success", false);
            response.put("message", "인증번호가 올바르지 않거나 만료되었습니다.");
            return ResponseEntity.badRequest().body(response);
        }

        // 5. 비밀번호 변경
        boolean passwordUpdated = authService.updatePassword(
                resetCompleteRequest.getUserId(),
                resetCompleteRequest.getNewPassword()
        );

        if (passwordUpdated) {
            response.put("success", true);
            response.put("message", "비밀번호가 성공적으로 변경되었습니다.");
            log.info("비밀번호 재설정 완료: {}", resetCompleteRequest.getUserId());
        } else {
            response.put("success", false);
            response.put("message", "비밀번호 변경에 실패했습니다.");
        }

        return ResponseEntity.ok(response);
    }



    //근데 .... 우리 로그아웃은 어떻게 하지...? 버튼이 없는데 ?
    @PostMapping("/logout")
    public ResponseEntity<Map<String, Object>> logout(HttpSession session) {
        session.invalidate();

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "로그아웃되었습니다.");

        return ResponseEntity.ok(response);
    }

    @GetMapping("/me")
    public ResponseEntity<Map<String, Object>> getCurrentUser(HttpSession session) {
        String userId = (String) session.getAttribute("userId");

        Map<String, Object> response = new HashMap<>();

        if (userId == null) {
            response.put("success", false);
            response.put("message", "로그인이 필요합니다.");
            return ResponseEntity.badRequest().body(response);
        }

        Optional<User> userOptional = authService.findByUserId(userId);

        if (userOptional.isEmpty()) {
            response.put("success", false);
            response.put("message", "사용자 정보를 찾을 수 없습니다.");
            return ResponseEntity.badRequest().body(response);
        }

        User user = userOptional.get();
        response.put("success", true);
        response.put("userId", user.getUserId());
        response.put("userName", user.getUserName());
        response.put("email", user.getEmail());
        response.put("phone", user.getPhone());
        response.put("userTypeCode", user.getUserTypeCode());

        return ResponseEntity.ok(response);
    }

    @GetMapping("/check/email/{email}")
    public ResponseEntity<Map<String, Object>> checkEmailDuplicate(@PathVariable String email) {
        boolean exists = authService.existsByEmail(email);

        Map<String, Object> response = new HashMap<>();
        response.put("exists", exists);
        response.put("message", exists ? "이미 사용중인 이메일입니다." : "사용 가능한 이메일입니다.");

        return ResponseEntity.ok(response);
    }



    //보안성 높게 처리하기 위해서 ( 별로면 삭제해도 됨 )

    //아이디 화면에 뿌리게 되면 아이디 마스킹 처리해서 화면서 일부만 보이게 하는거 .....
    private String maskUserId(String userId) {
        if (userId.length() <= 2) {
            return userId;
        }

        String prefix = userId.substring(0, 2);
        String suffix = userId.length() > 4 ? userId.substring(userId.length() - 2) : "";
        String masked = "*".repeat(Math.max(0, userId.length() - prefix.length() - suffix.length()));

        return prefix + masked + suffix;
    }

    //비밀번호 ( 피그마에 적힌양식대로 : 8~16자, 영문대소문자/숫자/특수문자)
    private String validatePassword(String password) {
        if (password == null || password.trim().isEmpty()) {
            return "비밀번호를 입력해주세요.";
        }

        if (password.length() < 8) {
            return "비밀번호는 8자 이상이어야 합니다.";
        }

        if (password.length() > 16) {
            return "비밀번호는 16자 이하여야 합니다.";
        }

        // 영문 대소문자, 숫자, 특수문자 포함 여부 검사
        boolean hasUpperCase = password.matches(".*[A-Z].*");
        boolean hasLowerCase = password.matches(".*[a-z].*");
        boolean hasDigit = password.matches(".*\\d.*");
        boolean hasSpecialChar = password.matches(".*[!@#$%^&*()_+\\-=\\[\\]{};':\"\\\\|,.<>/?].*");

        if (!hasUpperCase) {
            return "비밀번호는 영문 대문자를 포함해야 합니다.";
        }

        if (!hasLowerCase) {
            return "비밀번호는 영문 소문자를 포함해야 합니다.";
        }

        if (!hasDigit) {
            return "비밀번호는 숫자를 포함해야 합니다.";
        }

        if (!hasSpecialChar) {
            return "비밀번호는 특수문자(!@#$%^&* 등)를 포함해야 합니다.";
        }

        return null; // 검증 통과
    }

}
