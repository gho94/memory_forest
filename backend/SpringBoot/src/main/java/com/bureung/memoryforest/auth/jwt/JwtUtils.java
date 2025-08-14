package com.bureung.memoryforest.auth.jwt;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;
import java.util.UUID;

@Slf4j
@Component
public class JwtUtils {

    @Value("${jwt.secret}")
    private String jwtSecret;

    @Value("${jwt.access-token-expiration:900000}") // 15분
    private long accessTokenExpiration;

    @Value("${jwt.refresh-token-expiration:1209600000}") // 2주
    private long refreshTokenExpiration;

    @Value("${jwt.patient-token-expiration:86400000}") // 24시간 (환자 공유용)
    private long patientTokenExpiration;

    private SecretKey getSigningKey() {
        return Keys.hmacShaKeyFor(jwtSecret.getBytes());
    }

    // Access Token 생성 (15분)
    public String generateAccessToken(Long userId) {
        Date expiryDate = new Date(System.currentTimeMillis() + accessTokenExpiration);

        return Jwts.builder()
                .setSubject(userId.toString())
                .claim("type", "access")
                .setIssuedAt(new Date())
                .setExpiration(expiryDate)
                .signWith(getSigningKey())
                .compact();
    }

    // Refresh Token 생성 (2주)
    public String generateRefreshToken(Long userId) {
        Date expiryDate = new Date(System.currentTimeMillis() + refreshTokenExpiration);
        String tokenId = UUID.randomUUID().toString();

        return Jwts.builder()
                .setSubject(userId.toString())
                .claim("type", "refresh")
                .claim("tokenId", tokenId)
                .setIssuedAt(new Date())
                .setExpiration(expiryDate)
                .signWith(getSigningKey())
                .compact();
    }

    // 환자 공유용 Token 생성 (24시간)
    public String generatePatientToken(Long patientId) {
        Date expiryDate = new Date(System.currentTimeMillis() + patientTokenExpiration);

        return Jwts.builder()
                .setSubject(patientId.toString())
                .claim("type", "patient_share")
                .claim("patientId", patientId)
                .setIssuedAt(new Date())
                .setExpiration(expiryDate)
                .signWith(getSigningKey())
                .compact();
    }

    //String 버전 메서드 추가로 U0002 타입 문제 처리
    public String generateAccessToken(String userId) {
        Date expiryDate = new Date(System.currentTimeMillis() + accessTokenExpiration);

        return Jwts.builder()
                .setSubject(userId)
                .claim("type", "access")
                .setIssuedAt(new Date())
                .setExpiration(expiryDate)
                .signWith(getSigningKey())
                .compact();
    }

    public String generateRefreshToken(String userId) {
        Date expiryDate = new Date(System.currentTimeMillis() + refreshTokenExpiration);
        String tokenId = UUID.randomUUID().toString();

        return Jwts.builder()
                .setSubject(userId)
                .claim("type", "refresh")
                .claim("tokenId", tokenId)
                .setIssuedAt(new Date())
                .setExpiration(expiryDate)
                .signWith(getSigningKey())
                .compact();
    }


    // 토큰에서 사용자 ID 추출 -> string으로 바꿈
    public String getUserIdFromToken(String token) {
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claims.getSubject();
    }

    // 토큰에서 환자 ID 추출
    public String getPatientIdFromToken(String token) {
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claims.getSubject();
    }

    // 토큰 타입 확인
    public String getTokenType(String token) {
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claims.get("type", String.class);
    }

    // Refresh Token ID 추출
    public String getTokenId(String refreshToken) {
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(refreshToken)
                .getBody();
        return claims.get("tokenId", String.class);
    }

    // 토큰 유효성 검증
    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder()
                    .setSigningKey(getSigningKey())
                    .build()
                    .parseClaimsJws(token);
            return true;
        } catch (Exception e) {
            log.error("토큰 검증 실패: {}", e.getMessage());
            return false;
        }
    }

    // 토큰 만료 여부 확인
    public boolean isTokenExpired(String token) {
        try {
            Claims claims = Jwts.parserBuilder()
                    .setSigningKey(getSigningKey())
                    .build()
                    .parseClaimsJws(token)
                    .getBody();
            return claims.getExpiration().before(new Date());
        } catch (Exception e) {
            return true;
        }
    }

    //혹시라도 Long 타입 관련 에러 발생 방지용...
    public Long getUserIdFromTokenAsLong(String token) {
        String userId = getUserIdFromToken(token);
        try {
            return Long.parseLong(userId);
        } catch (NumberFormatException e) {
            log.error("사용자 ID를 Long으로 변환할 수 없음: {}", userId);
            throw new IllegalArgumentException("Invalid user ID format: " + userId);
        }
    }
}