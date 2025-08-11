package com.bureung.memoryforest.common.application;

import java.util.List;

import com.bureung.memoryforest.common.dto.request.CommonCodeRequestDto;
import com.bureung.memoryforest.common.dto.response.CommonCodeResponseDto;

public interface CommonCodeService {    
    List<CommonCodeResponseDto> getCommonCodesByParentCodeId(String parentCodeId);
    CommonCodeResponseDto getCommonCodeById(String codeId);
    CommonCodeResponseDto createCommonCode(CommonCodeRequestDto requestDto);
    CommonCodeResponseDto updateCommonCode(String codeId, CommonCodeRequestDto requestDto);
}
