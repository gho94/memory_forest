package com.bureung.memoryforest.common.application.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.bureung.memoryforest.common.application.CommonCodeService;
import com.bureung.memoryforest.common.domain.CommonCode;
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
    
}
