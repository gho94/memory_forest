package com.bureung.memoryforest.auth.application.impl;

import com.bureung.memoryforest.auth.application.PatientShareService;
import com.bureung.memoryforest.auth.application.RefreshTokenService;
import com.bureung.memoryforest.user.application.UserService;
import com.bureung.memoryforest.user.domain.User;
import com.bureung.memoryforest.auth.jwt.JwtUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class PatientShareServiceImpl implements PatientShareService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final JwtUtils jwtUtils;
    private final RefreshTokenService refreshTokenService;
    private final UserService userService;

    @Value("${app.base-url:http://localhost:3000}")
    private String baseUrl;

    @Value("${app.patient-share.link-expiration-hours:24}")
    private int linkExpirationHours;

    @Override
    public String generateShareLink(String patientId) {
        try {
            String accessCode = UUID.randomUUID().toString();
            String redisKey = "patient_access:" + accessCode;

            Map<String, String> patientInfo = new HashMap<>();
            patientInfo.put("patientId", patientId);


            String displayName = getPatientDisplayName(patientId);
            patientInfo.put("patientName", displayName);

            redisTemplate.opsForValue().set(redisKey, patientInfo, Duration.ofHours(linkExpirationHours));
            String shareUrl = baseUrl + "/patient-view/" + accessCode;

            log.info("환자 공유 링크 생성 완료 - 환자ID: {}, 접근코드: {}", patientId, displayName);
            return shareUrl;

        } catch (Exception e) {
            log.error("공유 링크 생성 실패 - 환자ID: {}", patientId, e);
            throw new RuntimeException("공유 링크 생성에 실패했습니다.");
        }
    }

    private String getPatientDisplayName(String patientId) {
        try {
            // UserService는 String userId를 받음
            Optional<User> userOptional = userService.findByUserId(patientId);

            if (userOptional.isPresent()) {
                User user = userOptional.get();
                String userName = user.getUserName();
                String loginId = user.getLoginId();

                // 우선순위: userName → loginId → 기본값
                if (userName != null && !userName.trim().isEmpty()) {
                    return userName;
                } else if (loginId != null && !loginId.trim().isEmpty()) {
                    return loginId;
                } else {
                    return "환자" + patientId;
                }
            } else {
                return "환자" + patientId;
            }

        } catch (Exception e) {
            log.warn("환자 정보 조회 실패, 기본값 사용 - 환자ID: {}", patientId, e);
            return "환자" + patientId;
        }
    }

    @Override
    public Map<String, Object> loginWithAccessCode(String accessCode) {
        try {
            String redisKey = "patient_access:" + accessCode;
            Object patientInfoObj = redisTemplate.opsForValue().get(redisKey);

            if (patientInfoObj == null) {
                log.warn("유효하지 않은 접근 코드: {}", accessCode);
                return null;
            }

            @SuppressWarnings("unchecked")
            Map<String, String> patientInfo = (Map<String, String>) patientInfoObj;
            String patientId = patientInfo.get("patientId");
            String patientName = patientInfo.get("patientName");

            if (patientId == null || patientId.trim().isEmpty()) {
                log.error("환자 ID 값 없음");
                return null;
            }
            log.info("==================>>>>> Redis에서 조회된 환자ID: {}, 표시명: {}", patientId, patientName);

            // 토큰 생성 (필요시에만)
            String accessToken = jwtUtils.generateAccessToken(patientId);
            String refreshToken = refreshTokenService.createRefreshToken(patientId);

            Map<String, Object> loginResult = new HashMap<>();
            loginResult.put("success", true);
            loginResult.put("accessToken", accessToken);
            loginResult.put("refreshToken", refreshToken);
            loginResult.put("patientId", patientId);
            loginResult.put("patientName", patientName);
            loginResult.put("isSharedAccess", true);

            // 일회성 코드 삭제
            redisTemplate.delete(redisKey);

            log.info("환자 로그인 성공 - 환자ID: {}, 표시명: {}, 접근코드: {}", patientId, patientName, accessCode);
            return loginResult;

        } catch (Exception e) {
            log.error("환자 로그인 실패 - 접근코드: {}", accessCode, e);
            return null;
        }
    }
}