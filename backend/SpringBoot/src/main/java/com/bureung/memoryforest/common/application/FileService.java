package com.bureung.memoryforest.common.application;

import com.bureung.memoryforest.common.dto.request.FileUploadRequestDto;
import com.bureung.memoryforest.common.dto.response.FileUploadResponseDto;

import org.springframework.web.multipart.MultipartFile;

public interface FileService {
    
    /**
     * S3에 파일 업로드
     */
    FileUploadResponseDto uploadFileToS3(MultipartFile file, FileUploadRequestDto uploadRequest);
    
    /**
     * 파일 ID로 파일 정보 조회
     */
    FileUploadResponseDto getFileById(Integer fileId);
}
