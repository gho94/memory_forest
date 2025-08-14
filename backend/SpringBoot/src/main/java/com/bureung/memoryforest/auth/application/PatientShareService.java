package com.bureung.memoryforest.auth.application;

import java.util.Map;

public interface PatientShareService {
    /**
     * 환자 공유 링크 생성 (24시간 유효)
     */
    String generateShareLink(Long patientId);

    /**
     * 접근 코드로 환자 로그인 처리 (15분 Access + 2주 Refresh 토큰 발급)
     * 환자 ID와 이름 정보만 반환 (기존 대시보드가 처리)
     */
    Map<String, Object> loginWithAccessCode(String accessCode);
}