package com.bureung.memoryforest.common.application;

import java.util.List;
import com.bureung.memoryforest.common.domain.CommonCode;

public interface CommonCodeService {
    
    /**
     * 모든 공통코드를 조회합니다.
     * @return 공통코드 목록
     */
    List<CommonCode> getAllCommonCodes();
}
