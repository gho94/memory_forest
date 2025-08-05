package com.bureung.memoryforest.common.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bureung.memoryforest.common.application.CommonCodeService;
import com.bureung.memoryforest.common.domain.CommonCode;

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
} 