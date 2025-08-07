package com.bureung.memoryforest.common.application.impl;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.bureung.memoryforest.common.application.CommonCodeService;
import com.bureung.memoryforest.common.domain.CommonCode;
import com.bureung.memoryforest.common.dto.request.CommonCodeRequestDto;
import com.bureung.memoryforest.common.dto.response.CommonCodeResDto;
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
        public List<CommonCodeResponseDto> getCommonCodes() {
        List<CommonCode> allCodes = commonCodeRepository.findAll();
        
        Map<String, CommonCodeResponseDto> codeMap = new HashMap<>();
        List<CommonCodeResponseDto> rootNodes = new ArrayList<>();
        
        for (CommonCode code : allCodes) {
            CommonCodeResponseDto treeNode = CommonCodeResponseDto.builder()
                    .id(code.getCodeID())
                    .label(code.getCodeName())
                    .parentCodeID(code.getParentCodeID())
                    .children(new ArrayList<>())
                    .build();
            
            codeMap.put(code.getCodeID(), treeNode);
        }
        
        for (CommonCodeResponseDto node : codeMap.values()) {
            if (node.getParentCodeID() == null || node.getParentCodeID().isEmpty()) {
                rootNodes.add(node);
            } else {
                CommonCodeResponseDto parent = codeMap.get(node.getParentCodeID());
                if (parent != null) {
                    parent.getChildren().add(node);
                }
            }
        }
        
        rootNodes.sort((a, b) -> a.getId().compareTo(b.getId()));
        for (CommonCodeResponseDto rootNode : rootNodes) {
            if (rootNode.getChildren() != null && !rootNode.getChildren().isEmpty()) {
                rootNode.getChildren().sort((a, b) -> a.getId().compareTo(b.getId()));
            }
        }
        
        return rootNodes;
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
                .id(savedCommonCode.getCodeID())
                .label(savedCommonCode.getCodeName())
                .parentCodeID(savedCommonCode.getParentCodeID())
                .build();
    }
    
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
                .id(updatedCode.getCodeID())
                .label(updatedCode.getCodeName())
                .parentCodeID(updatedCode.getParentCodeID())
                .useYn(updatedCode.getUseYn())
                .build();
    }


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

    @Override
    public List<CommonCodeResDto> getCommonCodesByParentCodeId(String parentCodeId) {
        List<CommonCode> commonCodes = commonCodeRepository.findByParentCodeIDOrderByCodeID(parentCodeId);
        
        return commonCodes.stream()
                .map(code -> CommonCodeResDto.builder()
                        .codeId(code.getCodeID())
                        .codeName(code.getCodeName())
                        .parentCodeId(code.getParentCodeID())
                        .useYn(code.getUseYn())
                        .build())
                .collect(Collectors.toList());
    }
}
