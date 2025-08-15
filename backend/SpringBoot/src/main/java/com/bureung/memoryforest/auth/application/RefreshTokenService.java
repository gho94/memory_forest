package com.bureung.memoryforest.auth.application;

public interface RefreshTokenService {
    /**
     * Refresh Token 생성
     */
    String createRefreshToken(Long userId);

    /**
     * Refresh Token 생성 (String 버전) - 공유 환자용
     */
    String createRefreshToken(String userId);

    /**
     * Refresh Token 유효성 검증
     */
    boolean validateRefreshToken(String refreshToken);

    /**
     * Refresh Token으로 새로운 Access Token 생성
     */
    String generateNewAccessToken(String refreshToken);

    /**
     * Refresh Token 삭제
     */
    void deleteRefreshToken(String refreshToken);

    /**
     * 사용자의 모든 Refresh Token 삭제
     */
    void deleteAllRefreshTokensByUserId(Long userId);

    /**
     * 사용자의 모든 Refresh Token 삭제 (String 버전)
     */
    void deleteAllRefreshTokensByUserId(String userId);
}