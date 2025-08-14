package com.bureung.memoryforest.auth.application.impl;

import com.bureung.memoryforest.auth.application.PatientShareService;
import com.bureung.memoryforest.auth.application.RefreshTokenService;
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
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class PatientShareServiceImpl implements PatientShareService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final JwtUtils jwtUtils;
    private final RefreshTokenService refreshTokenService;
    // 실제 환경에서 환자 이름이 필요하면:
    // private final UserService userService;

    @Value("${app.base-url:http://localhost:3000}")
    private String baseUrl;

    @Value("${app.patient-share.link-expiration-hours:24}")
    private int linkExpirationHours;

    @Override
    public String generateShareLink(String patientId) {
        try {
            String accessCode = UUID.randomUUID().toString();
            String redisKey = "patient_access:" + accessCode;
            redisTemplate.opsForValue().set(redisKey, patientId, Duration.ofHours(linkExpirationHours));
            String shareUrl = baseUrl + "/patient-view/" + accessCode;

            log.info("환자 공유 링크 생성 완료 - 환자ID: {}, 접근코드: {}", patientId, accessCode);
            return shareUrl;

        } catch (Exception e) {
            log.error("공유 링크 생성 실패 - 환자ID: {}", patientId, e);
            throw new RuntimeException("공유 링크 생성에 실패했습니다.");
        }
    }

    @Override
    public Map<String, Object> loginWithAccessCode(String accessCode) {
        try {
            String redisKey = "patient_access:" + accessCode;
            Object patientIdObj = redisTemplate.opsForValue().get(redisKey);

            if (patientIdObj == null) {
                log.warn("유효하지 않은 접근 코드: {}", accessCode);
                return null;
            }

//            Long patientId = convertToLong(patientIdObj);
            String patientId = patientIdObj.toString();
            if (patientId == null || patientId.trim().isEmpty()) {
                log.error("환자 ID 값 없음");
                return null;
            }
            log.info("==================>>>>> Redis에서 조회된 환자ID: {}", patientId);

            // DB에서 환자 이름 조회: String patientName = userService.findById(patientId).getUserName();
            String patientName = "환자" + patientId; // 임시

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

            log.info("환자 로그인 성공 - 환자ID: {}, 접근코드: {}", patientId, accessCode);
            return loginResult;

        } catch (Exception e) {
            log.error("환자 로그인 실패 - 접근코드: {}", accessCode, e);
            return null;
        }
    }

//    private Long convertToLong(Object obj) {
//        if (obj instanceof Integer) {
//            return ((Integer) obj).longValue();
//        } else if (obj instanceof Long) {
//            return (Long) obj;
//        } else if (obj instanceof String) {
//            try {
//                return Long.parseLong((String) obj);
//            } catch (NumberFormatException e) {
//                return null;
//            }
//        }
//        return null;
//    }
}