package com.bureung.memoryforest.auth.application.impl;

import com.bureung.memoryforest.auth.jwt.JwtUtils;
import com.bureung.memoryforest.auth.application.PatientShareService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class PatientShareServiceImpl implements PatientShareService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final JwtUtils jwtUtils;

    @Override
    public String generateShareLink(Long patientId) {
        // 1. 고유한 접근 코드 생성
        String accessCode = UUID.randomUUID().toString();

        // 2. Redis에 환자 ID 저장 (30일 유효)
        String redisKey = "patient_access:" + accessCode;
        redisTemplate.opsForValue().set(redisKey, patientId, Duration.ofDays(30));

        // 3. 공유 URL 생성
        String shareUrl = "http://localhost:8080/patient-view/" + accessCode;

        log.info("환자 공유 링크 생성 완료 - 환자ID: {}, 접근코드: {}", patientId, accessCode);
        return shareUrl;
    }

    @Override
    public String processPatientAccess(String accessCode) {
        String redisKey = "patient_access:" + accessCode;
        Long patientId = (Long) redisTemplate.opsForValue().get(redisKey);

        if (patientId == null) {
            log.warn("유효하지 않은 접근 코드: {}", accessCode);
            return null;
        }

        // JWT 토큰 생성
        String jwt = jwtUtils.generatePatientToken(patientId);
        log.info("환자 JWT 토큰 발급 완료 - 환자ID: {}", patientId);

        return jwt;
    }
}