package com.bureung.memoryforest.auth.application;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;


@Service
@RequiredArgsConstructor
@Slf4j
public class EmailService {

    private final JavaMailSender mailSender;

    // 인증번호 저장 (찾아보니까 Redis 사용 권장하는데 일단 메모리 사용으로 구현함)
//    private final Map<String, VerificationInfo> verificationCodes = new ConcurrentHashMap<>();

    private final Map<String, VerificationInfo> signupCodes = new ConcurrentHashMap<>();       // 회원가입용
    private final Map<String, VerificationInfo> findIdCodes = new ConcurrentHashMap<>();       // 아이디찾기용
    private final Map<String, VerificationInfo> passwordResetCodes = new ConcurrentHashMap<>(); // 비밀번호재설정용

    public static class EmailSendResult {
        private final boolean success;
        private final String message;
        private final long remainingSeconds; // 남은 시간 (초)

        private EmailSendResult(boolean success, String message, long remainingSeconds) {
            this.success = success;
            this.message = message;
            this.remainingSeconds = remainingSeconds;
        }

        public static EmailSendResult success() {
            return new EmailSendResult(true, "인증번호가 전송되었습니다.", 0);
        }

        public static EmailSendResult alreadySent(long remainingSeconds) {
            long minutes = remainingSeconds / 60;
            long seconds = remainingSeconds % 60;
            String timeMessage = minutes > 0 ?
                    String.format("%d분 %d초", minutes, seconds) :
                    String.format("%d초", seconds);
            return new EmailSendResult(false,
                    "이미 유효한 인증번호가 있습니다. " + timeMessage + " 후 다시 시도해주세요.",
                    remainingSeconds);
        }

        public static EmailSendResult failed() {
            return new EmailSendResult(false, "인증번호 전송에 실패했습니다.", 0);
        }

        // getters
        public boolean isSuccess() { return success; }
        public String getMessage() { return message; }
        public long getRemainingSeconds() { return remainingSeconds; }
    }

    // 이메일 인증번호 발송 ( 인증번호는 6자리의 랜덤번호로 생성함 ) - 회원가입
    public EmailSendResult sendVerificationCode(String email) {
        return sendVerificationCodeByType(email, signupCodes, "회원가입");
    }

    // 아이디 찾기
    public EmailSendResult sendFindIdVerificationCode(String email) {
        return sendVerificationCodeByType(email, findIdCodes, "아이디 찾기");
    }

    //비밀번호 찾기
    public EmailSendResult sendPasswordResetCode(String email) {
        return sendVerificationCodeByType(email, passwordResetCodes, "비밀번호 재설정");
    }

    private EmailSendResult sendVerificationCodeByType(String email, Map<String, VerificationInfo> targetMap, String purpose) {
        try {
            // 기존에 유효한 인증번호가 있는지 확인
//        VerificationInfo existingInfo = verificationCodes.get(email);
            VerificationInfo existingInfo = targetMap.get(email);
            if (existingInfo != null && LocalDateTime.now().isBefore(existingInfo.getExpiration())) {
                long remainingSeconds = java.time.Duration.between(LocalDateTime.now(), existingInfo.getExpiration()).getSeconds();
                log.info("이미 유효한 인증번호가 존재함: 이메일={}, 남은시간={}초", email, remainingSeconds);
                return EmailSendResult.alreadySent(remainingSeconds);
            }

            String code = generateVerificationCode();
            log.info("생성된 인증번호: {} (이메일: {})", code, email);

            // 이메일 발송 내용
            SimpleMailMessage message = new SimpleMailMessage();
            message.setTo(email);
            message.setSubject("[memory_forest] 이메일 인증번호");
            message.setText("안녕하세요. 동행자님 :) \n\n" +
                    "기억숲 이메일 인증번호는 다음과 같습니다.\n\n" +

                    "인증번호: " + code + "\n\n" +

                    "5분 이내에 입력해주세요.\n\n" +
                    "감사합니다.");

            mailSender.send(message);

            // 인증번호 저장 (5분 유효)
            LocalDateTime expiration = LocalDateTime.now().plusMinutes(5);
            targetMap.put(email, new VerificationInfo(code, expiration));
            log.info("{}용 인증번호 저장 완료: 이메일={}, 만료시간={}", purpose, email, expiration);

            log.info("현재 저장된 {}용 인증번호 개수: {}", purpose, targetMap.size());
            return EmailSendResult.success();
        } catch (Exception e) {
            log.error("{}용 인증번호 발송 실패: {}, 오류: {}", purpose, email, e.getMessage(), e);
            return EmailSendResult.failed();
        }
    }

    //인증번호 확인
    public boolean verifyCode(String email, String code) {
        return verifyCodeByType(email, code, signupCodes, "회원가입");
    }

    public boolean verifyFindIdCode(String email, String code) {
        return verifyCodeByType(email, code, findIdCodes, "아이디 찾기");
    }

    public boolean verifyPasswordResetCode(String email, String code) {
        return verifyCodeByType(email, code, passwordResetCodes, "비밀번호 재설정");
    }


    private boolean verifyCodeByType(String email, String code, Map<String, VerificationInfo> targetMap, String purpose) {
        log.info("{}용 인증번호 확인 시작: 이메일={}, 입력코드={}", purpose, email, code);

        VerificationInfo info = targetMap.get(email);
        if (info == null) {
            log.warn("{}용 인증정보 없음: {}", purpose, email);
            return false;
        }

        if (LocalDateTime.now().isAfter(info.getExpiration())) {
            log.warn("{}용 인증번호 만료: 이메일={}", purpose, email);
            targetMap.remove(email);
            return false;
        }

        if (info.getCode().equals(code)) {
            log.info("{}용 인증번호 일치: 이메일={}", purpose, email);
            targetMap.put(email, new VerificationInfo(code, info.getExpiration(), true));
            return true;
        } else {
            log.warn("{}용 인증번호 불일치: 이메일={}, 입력={}, 저장={}", purpose, email, code, info.getCode());
        }

        return false;
    }


    public boolean isEmailVerified(String email) {
        return isEmailVerifiedByType(email, signupCodes, "회원가입");
    }


    public boolean isFindIdEmailVerified(String email) {
        return isEmailVerifiedByType(email, findIdCodes, "아이디 찾기");
    }

    public boolean isPasswordResetEmailVerified(String email) {
        return isEmailVerifiedByType(email, passwordResetCodes, "비밀번호 재설정");
    }

    private boolean isEmailVerifiedByType(String email, Map<String, VerificationInfo> targetMap, String purpose) {
        VerificationInfo info = targetMap.get(email);
        boolean result = info != null && info.isVerified() && LocalDateTime.now().isBefore(info.getExpiration());
        log.info("{}용 이메일 인증 상태 확인: 이메일={}, 인증됨={}", purpose, email, result);
        return result;
    }


    // 아이디 찾기 - 아이디도 이메일으로 받을 수 있긴한뎅,,, 피그마에서는 그냥 화면에 뿌려주기로 해서 고민중
    public boolean sendUserIdEmail(String email, String userId) {
        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setTo(email);
            message.setSubject("[memory_forest] 아이디 찾기");
            message.setText("안녕하세요.\n\n" +
                    "회원가입 완료된 아이디를 알려드립니다.\n\n" +

                    "아이디: " + userId + "\n\n" +

                    "감사합니다.");

            mailSender.send(message);
            log.info("아이디 찾기 이메일 발송 성공: {}", email);
            return true;

        } catch (Exception e) {
            log.error("아이디 찾기 이메일 발송 실패: {}, 오류: {}", email, e.getMessage());
            return false;
        }
    }

    private String generateVerificationCode() {
        Random random = new Random();
        return String.format("%06d", random.nextInt(1000000));
    }

    // 인증번호 정보 저장 내부 클래스,,,,,,,,,,,,,,,어어어어어 졸려 왜 안돼 ㅠㅏㅏㅏㅏㅏ
    private static class VerificationInfo {
        private final String code;
        private final LocalDateTime expiration;
        private final boolean verified;

        public VerificationInfo(String code, LocalDateTime expiration) {
            this(code, expiration, false);
        }

        public VerificationInfo(String code, LocalDateTime expiration, boolean verified) {
            this.code = code;
            this.expiration = expiration;
            this.verified = verified;
        }

        public String getCode() { return code; }
        public LocalDateTime getExpiration() { return expiration; }
        public boolean isVerified() { return verified; }

        @Override
        public String toString() {
            return String.format("VerificationInfo{code='%s', expiration=%s, verified=%s}",
                    code, expiration, verified);
        }
    }
}