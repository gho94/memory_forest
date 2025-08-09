package com.bureung.memoryforest.common.application.impl;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.bureung.memoryforest.common.application.CommonCodeService;
import com.bureung.memoryforest.common.domain.CommonCode;
import com.bureung.memoryforest.common.dto.request.CommonCodeRequestDto;
import com.bureung.memoryforest.common.dto.response.CommonCodeResponseDto;
import com.bureung.memoryforest.common.repository.CommonCodeRepository;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
@Transactional(readOnly = true)
public class CommonCodeServiceImpl implements CommonCodeService {
    
    @Autowired
    CommonCodeRepository commonCodeRepository;
    
    @Override
    public List<CommonCodeResponseDto> getCommonCodesByParentCodeId(String parentCodeId) {
        List<CommonCode> commonCodes = commonCodeRepository.findByParentCodeIDOrderByCodeID(parentCodeId);
        
        return commonCodes.stream()
                .map(code -> CommonCodeResponseDto.builder()
                        .codeId(code.getCodeID())
                        .codeName(code.getCodeName())
                        .parentCodeId(code.getParentCodeID())
                        .useYn(code.getUseYn())
                        .build())
                .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public CommonCodeResponseDto createCommonCode(CommonCodeRequestDto requestDto) {  
        String parentCodeID = requestDto.getParentCodeID();      
        String codeID = generateCodeId(parentCodeID);

        CommonCode commonCode = CommonCode.builder()
                .codeID(codeID)
                .codeName(requestDto.getCodeName())
                .parentCodeID(parentCodeID)
                .useYn("Y")
                .createdBy("ADMIN")
                .build();
        
        CommonCode savedCommonCode = commonCodeRepository.save(commonCode);
        
        return CommonCodeResponseDto.builder()
                .codeId(savedCommonCode.getCodeID())
                .codeName(savedCommonCode.getCodeName())
                .parentCodeId(savedCommonCode.getParentCodeID())
                .useYn(savedCommonCode.getUseYn())
                .build();
    }

    //#region 공통 코드 ID 생성
    private String generateCodeId(String parentCodeId) {
        String header;
        
        if (parentCodeId == null) {
            header = selectLastCodeHeader();
        } else {
            char firstChar = parentCodeId.charAt(0);
            header = String.valueOf(firstChar) + (Integer.parseInt(parentCodeId.substring(1, 2)) + 1);
        }
        
        return createLastCodeId(header);
    }
    
    private String createLastCodeId(String header) {
        String lastCodeId = commonCodeRepository.findLastCodeIdByHeader(header);
        
        String codeId = header + "0001";
        
        if (lastCodeId != null && !lastCodeId.isEmpty()) {
            String lastNumberStr = lastCodeId.substring(header.length());
            int lastNumber = Integer.parseInt(lastNumberStr);
            codeId = header + String.format("%04d", lastNumber + 1);
        }
        
        return codeId;
    }

    private String selectLastCodeHeader() {
        String lastCodeId = commonCodeRepository.findLastCodeId();        
        String codeHeader = "A0";
        
        if (lastCodeId != null && !lastCodeId.isEmpty()) {
            char firstChar = lastCodeId.charAt(0);
            char nextChar = (char) (firstChar + 1);
            codeHeader = String.valueOf(nextChar) + "0";
        }
        
        return codeHeader;
    }
    //#endregion
    
    @Override
    @Transactional
    public CommonCodeResponseDto updateCommonCode(String codeId, CommonCodeRequestDto requestDto) {
        CommonCode existingCode = commonCodeRepository.findById(codeId)
                .orElseThrow(() -> new IllegalArgumentException("코드를 찾을 수 없습니다: " + codeId));
        
        existingCode.setCodeName(requestDto.getCodeName());
        existingCode.setUseYn(requestDto.getUseYn() == null ? "Y" : requestDto.getUseYn());
        existingCode.setUpdatedBy("ADMIN");
        
        CommonCode updatedCode = commonCodeRepository.save(existingCode);
        
        return CommonCodeResponseDto.builder()
                .codeId(updatedCode.getCodeID())
                .codeName(updatedCode.getCodeName())
                .parentCodeId(updatedCode.getParentCodeID())
                .useYn(updatedCode.getUseYn())
                .build();
    }
}
