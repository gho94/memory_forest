package com.bureung.memoryforest.common.application;

import java.util.List;
import com.bureung.memoryforest.common.domain.CommonCode;
import com.bureung.memoryforest.common.dto.request.CommonCodeCreateRequestDto;
import com.bureung.memoryforest.common.dto.response.CommonCodeResponseDto;

public interface CommonCodeService {
    
    /**
     * 모든 공통코드를 조회합니다.
     * @return 공통코드 목록
     */
    List<CommonCode> getAllCommonCodes();
    
    /**
     * 공통코드를 생성합니다.
     * @param requestDto 생성할 공통코드 정보
     * @return 생성된 공통코드 정보
     */
    CommonCodeResponseDto createCommonCode(CommonCodeCreateRequestDto requestDto);
}
