 package com.bureung.memoryforest.auth.controller;

 import com.bureung.memoryforest.auth.application.AuthService;
 import com.bureung.memoryforest.auth.application.EmailService;
 import com.bureung.memoryforest.auth.dto.request.*;
 import com.bureung.memoryforest.auth.dto.response.LoginResponseDto;
 import com.bureung.memoryforest.auth.dto.response.JoinResponseDto;
 import com.bureung.memoryforest.auth.dto.request.FindIdWithVerificationRequestDto;
 import com.bureung.memoryforest.auth.dto.request.PasswordResetVerifyRequestDto;
 import com.bureung.memoryforest.user.domain.User;
 import lombok.RequiredArgsConstructor;
 import lombok.extern.slf4j.Slf4j;
 import org.springframework.http.ResponseEntity;
 import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
 import org.springframework.security.core.Authentication;
 import org.springframework.security.core.context.SecurityContextHolder;
 import org.springframework.web.bind.annotation.*;
 import jakarta.servlet.http.HttpServletRequest; //session 추가
 import org.springframework.http.HttpStatus;  //session 추가

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

     //로그인
     @PostMapping("/login")
//     public ResponseEntity<Map<String, Object>> login(@RequestBody LoginRequestDto loginRequest, HttpSession session) {
     public ResponseEntity<Map<String, Object>> login(@RequestBody LoginRequestDto loginRequest, HttpServletRequest request) {
         LoginResponseDto result = authService.login(loginRequest.getLoginId(), loginRequest.getPassword());

         Map<String, Object> response = new HashMap<>();

         if (!result.isSuccess()) {
             response.put("success", false);
             response.put("message", result.getMessage());
             return ResponseEntity.badRequest().body(response);
         }

         User user = result.getUser();
         HttpSession oldSession = request.getSession(false);
         if (oldSession != null) {
             oldSession.invalidate();
         }

         SecurityContextHolder.clearContext();

        // 새로운 세션 생성
         HttpSession session = request.getSession(true);

         // Security Context에 인증 정보 설정
         UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(user, null, user.getAuthorities());
         SecurityContextHolder.getContext().setAuthentication(authToken);

         session.setAttribute("userId", user.getUserId());
         session.setAttribute("loginId", user.getLoginId());
         session.setAttribute("userTypeCode", user.getUserTypeCode());
         session.setAttribute("userName", user.getUserName());
         session.setAttribute("loginType", user.getLoginType());

         response.put("success", true);
         response.put("message", "로그인 성공");
         response.put("userId", user.getUserId());
         response.put("loginId", user.getLoginId());
         response.put("userName", user.getUserName());
         response.put("userTypeCode", user.getUserTypeCode());
         response.put("email", user.getEmail());
         response.put("loginType", user.getLoginType());

         return ResponseEntity.ok(response);
     }

     //회원가입
     // 1. 아이디 중복 체크
     @GetMapping("/check/userid")
     public ResponseEntity<Map<String, Object>> checkLoginIdDuplicate(@RequestParam("loginId") String loginId) {
         boolean exists = authService.existsByLoginId(loginId);

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


         EmailService.EmailSendResult result = emailService.sendVerificationCode(emailRequest.getEmail());

         response.put("success", result.isSuccess());
         response.put("message", result.getMessage());

         // 남은 시간이 있으면 추가 정보 제공
         if (result.getRemainingSeconds() > 0) {
             response.put("remainingSeconds", result.getRemainingSeconds());
         }
         return result.isSuccess() ?
                 ResponseEntity.ok(response) :
                 ResponseEntity.badRequest().body(response);
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
         log.info("회원가입 요청 - 이메일: {}, 아이디: {}", signupRequest.getEmail(), signupRequest.getLoginId());

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
     @PostMapping("/findId/email/send")
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

         EmailService.EmailSendResult result = emailService.sendFindIdVerificationCode(emailRequest.getEmail());

         response.put("success", result.isSuccess());
         response.put("message", result.getMessage());

         if (result.getRemainingSeconds() > 0) {
             response.put("remainingSeconds", result.getRemainingSeconds());
         }

         return result.isSuccess() ?
                 ResponseEntity.ok(response) :
                 ResponseEntity.badRequest().body(response);
     }

     // 2. 아이디 찾기 (인증번호 확인 후)
     @PostMapping("/findId")
     public ResponseEntity<Map<String, Object>> findUserId(@RequestBody FindIdWithVerificationRequestDto findIdRequest) {
         log.info("아이디 찾기 요청: {}", findIdRequest.getEmail());

         Map<String, Object> response = new HashMap<>();

         // 1. 인증번호 확인
         boolean isValidCode = emailService.verifyFindIdCode(findIdRequest.getEmail(), findIdRequest.getCode());
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
         //수정0811
         String maskedLoginId  = maskLoginId(user.getLoginId());

         response.put("success", true);
         response.put("message", "아이디를 찾았습니다.");
         response.put("loginId", maskedLoginId);
         response.put("fullLoginId", user.getLoginId()); // 프론트에서 필요시 사용

         log.info("아이디 찾기 성공: {} -> {}", findIdRequest.getEmail(), maskedLoginId);
         return ResponseEntity.ok(response);
     }

     //비밀번호 찾기
     // 1. 비밀번호 재설정 인증번호 발송
     @PostMapping("/password/reset/send")
     public ResponseEntity<Map<String, Object>> sendPasswordResetCode(@RequestBody PasswordResetRequestDto resetRequest) {
         log.info("비밀번호 재설정 인증번호 발송 요청: {} / {}", resetRequest.getLoginId(), resetRequest.getEmail());

         Map<String, Object> response = new HashMap<>();

         // 아이디와 이메일로 사용자 찾기
         Optional<User> userOptional = authService.findByLoginIdAndEmail(
                 resetRequest.getLoginId(),
                 resetRequest.getEmail()
         );

         if (userOptional.isEmpty()) {
             response.put("success", false);
             response.put("message", "입력하신 아이디와 이메일이 일치하지 않습니다.");
             return ResponseEntity.badRequest().body(response);
         }

         // 비밀번호 재설정용 인증번호 발송
         EmailService.EmailSendResult result = emailService.sendPasswordResetCode(resetRequest.getEmail());

         response.put("success", result.isSuccess());
         response.put("message", result.getMessage());

         if (result.getRemainingSeconds() > 0) {
             response.put("remainingSeconds", result.getRemainingSeconds());
         }

         return result.isSuccess() ?
                 ResponseEntity.ok(response) :
                 ResponseEntity.badRequest().body(response);
     }


     // 2. 비밀번호 인증 확인
     @PostMapping("/password/reset/verify")
     public ResponseEntity<Map<String, Object>> verifyPasswordResetCode(@RequestBody PasswordResetVerifyRequestDto verifyRequest) {
         log.info("비밀번호 재설정 인증번호 검증 요청: {} / {}", verifyRequest.getLoginId(), verifyRequest.getEmail());

         Map<String, Object> response = new HashMap<>();

         // 1. 아이디와 이메일로 사용자 존재 확인
         Optional<User> userOptional = authService.findByLoginIdAndEmail(
                 verifyRequest.getLoginId(),
                 verifyRequest.getEmail()
         );

         if (userOptional.isEmpty()) {
             response.put("success", false);
             response.put("message", "입력하신 아이디와 이메일이 일치하지 않습니다.");
             return ResponseEntity.badRequest().body(response);
         }

         // 2. 인증번호 확인
         boolean isValidCode = emailService.verifyPasswordResetCode(verifyRequest.getEmail(), verifyRequest.getCode());
         if (!isValidCode) {
             response.put("success", false);
             response.put("message", "인증번호가 올바르지 않거나 만료되었습니다.");
             return ResponseEntity.badRequest().body(response);
         }

         // 3. 인증 성공
         response.put("success", true);
         response.put("message", "인증이 완료되었습니다. 새 비밀번호를 설정해주세요.");

         log.info("비밀번호 재설정 인증번호 검증 성공: {}", verifyRequest.getLoginId());
         return ResponseEntity.ok(response);
     }

     // 3. 비밀번호 재설정 완료
     @PostMapping("/password/reset/complete")
     public ResponseEntity<Map<String, Object>> completePasswordReset(@RequestBody PasswordResetCompleteRequestDto resetCompleteRequest) {
         log.info("비밀번호 재설정 완료 요청: {} / {}", resetCompleteRequest.getLoginId(), resetCompleteRequest.getEmail());

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
         Optional<User> userOptional = authService.findByLoginIdAndEmail(
                 resetCompleteRequest.getLoginId(),
                 resetCompleteRequest.getEmail()
         );

         if (userOptional.isEmpty()) {
             response.put("success", false);
             response.put("message", "입력하신 아이디와 이메일이 일치하지 않습니다.");
             return ResponseEntity.badRequest().body(response);
         }

         // 4. 인증번호 확인
         boolean isValidCode = emailService.verifyPasswordResetCode(resetCompleteRequest.getEmail(), resetCompleteRequest.getCode());
         if (!isValidCode) {
             response.put("success", false);
             response.put("message", "인증번호가 올바르지 않거나 만료되었습니다.");
             return ResponseEntity.badRequest().body(response);
         }

         // 5. 비밀번호 변경
         boolean passwordUpdated = authService.updatePassword(
                 resetCompleteRequest.getLoginId(),
                 resetCompleteRequest.getNewPassword()
         );

         if (passwordUpdated) {
             response.put("success", true);
             response.put("message", "비밀번호가 성공적으로 변경되었습니다.");
             log.info("비밀번호 재설정 완료: {}", resetCompleteRequest.getLoginId());
         } else {
             response.put("success", false);
             response.put("message", "비밀번호 변경에 실패했습니다.");
         }

         return ResponseEntity.ok(response);
     }



     //근데 .... 우리 로그아웃은 어떻게 하지...? 버튼이 없는데 ?
     @PostMapping("/logout")
     public ResponseEntity<Map<String, Object>> logout(HttpSession session) {
         SecurityContextHolder.clearContext(); //시큐리티 context 정리,,, 이거 추가해야한다고 함...0810
         session.invalidate(); //세션 무효화 처리

         Map<String, Object> response = new HashMap<>();

         response.put("success", true);
         response.put("message", "로그아웃되었습니다.");
         return ResponseEntity.ok(response);
     }

     //나의 정보들 뿌릴 수 있는 api - 가족 마이페이지 ? + 탈퇴 + 로그아웃 구현 시 사용 예정으로 만들었음
     @GetMapping("/me")
     public ResponseEntity<Map<String, Object>> getCurrentUser(HttpSession session) {
         String userId = (String) session.getAttribute("userId");


         //이 부분도 시큐리티 context 정리,,, 이거 추가해야한다고 함... 0810
         Authentication auth = SecurityContextHolder.getContext().getAuthentication();
         if (auth != null && auth.getPrincipal() instanceof User) {
             User user = (User) auth.getPrincipal();
             userId = user.getUserId();
         }

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
         response.put("loginId", user.getLoginId()); // 0811 추가
         response.put("userName", user.getUserName());
         response.put("email", user.getEmail());
         response.put("phone", user.getPhone());
         response.put("userTypeCode", user.getUserTypeCode());
         response.put("loginType", user.getLoginType());

         return ResponseEntity.ok(response);
     }


     @GetMapping("/session-info")
     public ResponseEntity<Map<String, Object>> getSessionInfo(HttpServletRequest request) {
         try {
             HttpSession session = request.getSession(false);

             if (session == null) {
                 Map<String, Object> errorResponse = new HashMap<>();
                 errorResponse.put("success", false);
                 errorResponse.put("message", "세션이 없습니다.");
                 return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(errorResponse);
             }

             String userId = (String) session.getAttribute("userId");
             String userName = (String) session.getAttribute("userName");
             String userTypeCode = (String) session.getAttribute("userTypeCode");
             String loginType = (String) session.getAttribute("loginType");
             String loginId = (String) session.getAttribute("loginId");

             if (userId == null) {
                 Map<String, Object> errorResponse = new HashMap<>();
                 errorResponse.put("success", false);
                 errorResponse.put("message", "로그인이 필요합니다.");
                 return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(errorResponse);
             }

             Map<String, Object> response = new HashMap<>();
             response.put("success", true);
             response.put("userId", userId);
             response.put("userName", userName != null ? userName : "");
             response.put("userTypeCode", userTypeCode != null ? userTypeCode : "");
             response.put("loginType", loginType != null ? loginType : "DEFAULT");
             response.put("loginId", loginId != null ? loginId : "");

             // 추가 정보가 필요하면 User 조회
             Optional<User> userOptional = authService.findByUserId(userId);
             if (userOptional.isPresent()) {
                 User user = userOptional.get();
                 response.put("email", user.getEmail() != null ? user.getEmail() : "");
                 response.put("phone", user.getPhone() != null ? user.getPhone() : "");
             }

             log.info("세션 정보 조회 성공: {}", userId);
             return ResponseEntity.ok(response);

         } catch (Exception e) {
             log.error("세션 정보 조회 중 오류: ", e);
             Map<String, Object> errorResponse = new HashMap<>();
             errorResponse.put("success", false);
             errorResponse.put("message", "서버 오류가 발생했습니다.");
             return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
         }
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
     private String maskLoginId(String loginId) {
         if (loginId.length() <= 2) {
             return loginId;
         }
         String prefix = loginId.substring(0, 2);
         String suffix = loginId.length() > 4 ? loginId.substring(loginId.length() - 2) : "";
         String masked = "*".repeat(Math.max(0, loginId.length() - prefix.length() - suffix.length()));
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
