package com.bureung.memoryforest.common.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.bureung.memoryforest.common.application.CommonCodeService;
import com.bureung.memoryforest.common.dto.request.CommonCodeRequestDto;
import com.bureung.memoryforest.common.dto.response.CommonCodeResponseDto;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@RestController
@RequestMapping("/api/common-codes")
public class CommonCodeController {
    
    @Autowired
    CommonCodeService commonCodeService;

    @GetMapping
    public ResponseEntity<List<CommonCodeResponseDto>> getCommonCodesByParentCodeId(
            @RequestParam(required = false) String parentCodeID) {
        log.info("공통코드 조회 API 호출: parentCodeID={}", parentCodeID);
        try {
            List<CommonCodeResponseDto> commonCodes = commonCodeService.getCommonCodesByParentCodeId(parentCodeID);
            log.info("공통코드 조회 완료");
            return ResponseEntity.ok(commonCodes);
        } catch (Exception e) {
            log.error("공통코드 조회 중 오류 발생", e);
            return ResponseEntity.internalServerError().build();
        }
    }

    @GetMapping("/{codeId}")
    public ResponseEntity<CommonCodeResponseDto> getCommonCodeById(@PathVariable String codeId) {
        log.info("공통코드 개별 조회 API 호출: codeId={}", codeId);
        try {
            CommonCodeResponseDto commonCode = commonCodeService.getCommonCodeById(codeId);
            if (commonCode != null) {
                log.info("공통코드 개별 조회 완료");
                return ResponseEntity.ok(commonCode);
            } else {
                log.warn("공통코드를 찾을 수 없음: codeId={}", codeId);
                return ResponseEntity.notFound().build();
            }
        } catch (Exception e) {
            log.error("공통코드 개별 조회 중 오류 발생", e);
            return ResponseEntity.internalServerError().build();
        }
    }

    @PostMapping
    public ResponseEntity<CommonCodeResponseDto> createCommonCode(@RequestBody CommonCodeRequestDto requestDto) {
        log.info("공통코드 생성 API 호출: {}", requestDto);
        try {
            CommonCodeResponseDto responseDto = commonCodeService.createCommonCode(requestDto);
            return ResponseEntity.ok(responseDto);
        } catch (IllegalArgumentException e) {
            log.error("공통코드 생성 중 유효성 검사 오류: {}", e.getMessage());
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            log.error("공통코드 생성 중 오류 발생", e);
            return ResponseEntity.internalServerError().build();
        }
    }
    
    @PutMapping("/{codeId}")
    public ResponseEntity<CommonCodeResponseDto> updateCommonCode(
            @PathVariable String codeId, 
            @RequestBody CommonCodeRequestDto requestDto) {
        log.info("공통코드 수정 API 호출: codeId={}, requestDto={}", codeId, requestDto);
        try {
            CommonCodeResponseDto responseDto = commonCodeService.updateCommonCode(codeId, requestDto);
            return ResponseEntity.ok(responseDto);
        } catch (IllegalArgumentException e) {
            log.error("공통코드 수정 중 유효성 검사 오류: {}", e.getMessage());
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            log.error("공통코드 수정 중 오류 발생", e);
            return ResponseEntity.internalServerError().build();
        }
    }

} 