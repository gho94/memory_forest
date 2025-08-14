package com.bureung.memoryforest.auth.application.impl;

import com.bureung.memoryforest.auth.application.RefreshTokenService;
import com.bureung.memoryforest.auth.jwt.JwtUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.Set;

@Slf4j
@Service
@RequiredArgsConstructor
public class RefreshTokenServiceImpl implements RefreshTokenService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final JwtUtils jwtUtils;

    @Override
    public String createRefreshToken(Long userId) {
        try {
            String refreshToken = jwtUtils.generateRefreshToken(userId);
            String tokenId = jwtUtils.getTokenId(refreshToken);

            // Redis에 Refresh Token 저장 (2주)
            String redisKey = "refresh_token:" + tokenId;
            redisTemplate.opsForValue().set(redisKey, userId, Duration.ofDays(14));

            // 사용자별 토큰 목록 관리
            String userTokensKey = "user_tokens:" + userId;
            redisTemplate.opsForSet().add(userTokensKey, tokenId);
            redisTemplate.expire(userTokensKey, Duration.ofDays(14));

            log.info("Refresh Token 생성 완료 - 사용자ID: {}, 토큰ID: {}", userId, tokenId);
            return refreshToken;

        } catch (Exception e) {
            log.error("Refresh Token 생성 실패 - 사용자ID: {}", userId, e);
            throw new RuntimeException("Refresh Token 생성에 실패했습니다.");
        }
    }

    @Override
    public boolean validateRefreshToken(String refreshToken) {
        try {
            if (!jwtUtils.validateToken(refreshToken)) {
                return false;
            }

            String tokenType = jwtUtils.getTokenType(refreshToken);
            if (!"refresh".equals(tokenType)) {
                return false;
            }

            String tokenId = jwtUtils.getTokenId(refreshToken);
            String redisKey = "refresh_token:" + tokenId;

            return redisTemplate.hasKey(redisKey);

        } catch (Exception e) {
            log.error("Refresh Token 검증 실패", e);
            return false;
        }
    }

    @Override
    public String generateNewAccessToken(String refreshToken) {
        try {
            if (!validateRefreshToken(refreshToken)) {
                throw new RuntimeException("유효하지 않은 Refresh Token입니다.");
            }

            Long userId = jwtUtils.getUserIdFromToken(refreshToken);
            return jwtUtils.generateAccessToken(userId);

        } catch (Exception e) {
            log.error("새로운 Access Token 생성 실패", e);
            throw new RuntimeException("Access Token 생성에 실패했습니다.");
        }
    }

    @Override
    public void deleteRefreshToken(String refreshToken) {
        try {
            String tokenId = jwtUtils.getTokenId(refreshToken);
            Long userId = jwtUtils.getUserIdFromToken(refreshToken);

            // Redis에서 토큰 삭제
            String redisKey = "refresh_token:" + tokenId;
            redisTemplate.delete(redisKey);

            // 사용자 토큰 목록에서도 삭제
            String userTokensKey = "user_tokens:" + userId;
            redisTemplate.opsForSet().remove(userTokensKey, tokenId);

            log.info("Refresh Token 삭제 완료 - 사용자ID: {}, 토큰ID: {}", userId, tokenId);

        } catch (Exception e) {
            log.error("Refresh Token 삭제 실패", e);
        }
    }

    @Override
    public void deleteAllRefreshTokensByUserId(Long userId) {
        try {
            String userTokensKey = "user_tokens:" + userId;
            Set<Object> tokenIds = redisTemplate.opsForSet().members(userTokensKey);

            if (tokenIds != null) {
                for (Object tokenId : tokenIds) {
                    String redisKey = "refresh_token:" + tokenId;
                    redisTemplate.delete(redisKey);
                }
            }

            redisTemplate.delete(userTokensKey);
            log.info("사용자의 모든 Refresh Token 삭제 완료 - 사용자ID: {}", userId);

        } catch (Exception e) {
            log.error("사용자의 모든 Refresh Token 삭제 실패 - 사용자ID: {}", userId, e);
        }
    }
}