package com.bureung.memoryforest.common.application.impl;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.bureung.memoryforest.common.application.CommonCodeService;
import com.bureung.memoryforest.common.domain.CommonCode;
import com.bureung.memoryforest.common.dto.request.CommonCodeCreateRequestDto;
import com.bureung.memoryforest.common.dto.response.CommonCodeResponseDto;
import com.bureung.memoryforest.common.repository.CommonCodeRepository;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
@Transactional(readOnly = true)
public class CommonCodeServiceImpl implements CommonCodeService {
    
    private final CommonCodeRepository commonCodeRepository;
    
    @Autowired
    public CommonCodeServiceImpl(CommonCodeRepository commonCodeRepository) {
        this.commonCodeRepository = commonCodeRepository;
    }
    
    @Override
    public List<CommonCode> getAllCommonCodes() {
        log.info("모든 공통코드 조회 요청");
        List<CommonCode> commonCodes = commonCodeRepository.findAll();
        log.info("조회된 공통코드 개수: {}", commonCodes.size());
        return commonCodes;
    }
    
    @Override
    @Transactional
    public CommonCodeResponseDto createCommonCode(CommonCodeCreateRequestDto requestDto) {
        log.info("공통코드 생성 요청: {}", requestDto);
        
        // 중복 체크
        if (commonCodeRepository.existsById(requestDto.getCodeID())) {
            throw new IllegalArgumentException("이미 존재하는 코드 ID입니다: " + requestDto.getCodeID());
        }
        
        // CommonCode 엔티티 생성
        CommonCode commonCode = CommonCode.builder()
                .codeID(requestDto.getCodeID())
                .codeName(requestDto.getCodeName())
                .parentCodeID(requestDto.getParentCodeID())
                .userYn(requestDto.getUserYn())
                .createdBy(requestDto.getCreatedBy())
                .createdAt(LocalDateTime.now())
                .build();
        
        // 저장
        CommonCode savedCommonCode = commonCodeRepository.save(commonCode);
        log.info("공통코드 생성 완료: {}", savedCommonCode.getCodeID());
        
        // 응답 DTO 생성
        return CommonCodeResponseDto.builder()
                .codeID(savedCommonCode.getCodeID())
                .codeName(savedCommonCode.getCodeName())
                .parentCodeID(savedCommonCode.getParentCodeID())
                .userYn(savedCommonCode.getUserYn())
                .createdBy(savedCommonCode.getCreatedBy())
                .createdAt(savedCommonCode.getCreatedAt())
                .updatedBy(savedCommonCode.getUpdatedBy())
                .updatedAt(savedCommonCode.getUpdatedAt())
                .build();
    }
}
