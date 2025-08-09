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
    private final Map<String, VerificationInfo> verificationCodes = new ConcurrentHashMap<>();

    // 이메일 인증번호 발송 ( 인증번호는 6자리의 랜덤번호로 생성함 )
    public boolean sendVerificationCode(String email) {
        try {
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
            verificationCodes.put(email, new VerificationInfo(code, expiration));
            log.info("인증번호 저장 완료: 이메일={}, 만료시간={}", email, expiration);

            log.info("현재 저장된 인증번호 개수: {}", verificationCodes.size());
            return true;
        } catch (Exception e) {
            log.error("인증번호 발송 실패: {}, 오류: {}", email, e.getMessage(), e);
            return false;
        }
    }

    // 인증번호 확인
    public boolean verifyCode(String email, String code) {
        log.info("인증번호 확인 시작: 이메일={}, 입력코드={}", email, code);

        VerificationInfo info = verificationCodes.get(email);
        log.info("저장된 인증정보: {}", info != null ? "존재함" : "없음");

        if (info == null) {
            log.warn("인증정보 없음: {}", email);
            return false;
        }

        log.info("저장된 코드: {}, 만료시간: {}", info.getCode(), info.getExpiration());
        log.info("현재시간: {}", LocalDateTime.now());

        if (LocalDateTime.now().isAfter(info.getExpiration())) {
            log.warn("인증번호 만료: 이메일={}", email);
            verificationCodes.remove(email); // 유효시간 만료니까 삭제하고
            return false; // 시간 만료
        }

        if (info.getCode().equals(code)) {
            log.info("인증번호 일치: 이메일={}", email);

            // 인증 성공이면 ->  인증 완료 상태로 변경
            verificationCodes.put(email, new VerificationInfo(code, info.getExpiration(), true));
            log.info("인증 완료 상태로 변경: 이메일={}", email);
            return true;
        } else {
            log.warn("인증번호 불일치: 이메일={}, 입력={}, 저장={}", email, code, info.getCode());
        }

        return false; // 메일으로 보낸 인증번호랑 불일치하는 경우
    }

    // 이메일 인증 완료 여부 확인
    public boolean isEmailVerified(String email) {
        VerificationInfo info = verificationCodes.get(email);
        boolean result = info != null && info.isVerified() && LocalDateTime.now().isBefore(info.getExpiration());
        log.info("이메일 인증 상태 확인: 이메일={}, 인증됨={}", email, result);

        if (info != null) {
            log.info("인증정보 상세: 코드={}, 인증됨={}, 만료시간={}",
                    info.getCode(), info.isVerified(), info.getExpiration());
        }

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

    // 비밀번호 재설정 인증번호 발송
    public boolean sendPasswordResetCode(String email) {
        return sendVerificationCode(email); // 동일한 로직 재사용
    }

    private String generateVerificationCode() {
        Random random = new Random();
        return String.format("%06d", random.nextInt(1000000));
    }

    // 디버깅
    public void logStoredVerificationCodes() {
        log.info("=== 저장된 인증번호 목록 ===");
        verificationCodes.forEach((email, info) -> {
            log.info("이메일: {}, 코드: {}, 인증됨: {}, 만료시간: {}",
                    email, info.getCode(), info.isVerified(), info.getExpiration());
        });
        log.info("=== 총 {} 개 ===", verificationCodes.size());
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
