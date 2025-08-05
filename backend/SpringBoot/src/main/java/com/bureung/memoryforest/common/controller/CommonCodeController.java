package com.bureung.memoryforest.common.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bureung.memoryforest.common.application.CommonCodeService;
import com.bureung.memoryforest.common.domain.CommonCode;
import com.bureung.memoryforest.common.dto.request.CommonCodeCreateRequestDto;
import com.bureung.memoryforest.common.dto.response.CommonCodeResponseDto;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@RestController
@RequestMapping("/api/common-codes")
public class CommonCodeController {
    
    private final CommonCodeService commonCodeService;
    
    @Autowired
    public CommonCodeController(CommonCodeService commonCodeService) {
        this.commonCodeService = commonCodeService;
    }
    
    /**
     * 모든 공통코드 조회
     */
    @GetMapping
    public ResponseEntity<List<CommonCode>> getAllCommonCodes() {
        log.info("모든 공통코드 조회 API 호출");
        try {
            List<CommonCode> commonCodes = commonCodeService.getAllCommonCodes();
            log.info("조회된 공통코드 개수: {}", commonCodes.size());
            return ResponseEntity.ok(commonCodes);
        } catch (Exception e) {
            log.error("공통코드 조회 중 오류 발생", e);
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 공통코드 생성
     */
    @PostMapping
    public ResponseEntity<CommonCodeResponseDto> createCommonCode(@RequestBody CommonCodeCreateRequestDto requestDto) {
        log.info("공통코드 생성 API 호출: {}", requestDto);
        try {
            CommonCodeResponseDto responseDto = commonCodeService.createCommonCode(requestDto);
            log.info("공통코드 생성 완료: {}", responseDto.getCodeID());
            return ResponseEntity.ok(responseDto);
        } catch (IllegalArgumentException e) {
            log.error("공통코드 생성 중 유효성 검사 오류: {}", e.getMessage());
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            log.error("공통코드 생성 중 오류 발생", e);
            return ResponseEntity.internalServerError().build();
        }
    }
} 