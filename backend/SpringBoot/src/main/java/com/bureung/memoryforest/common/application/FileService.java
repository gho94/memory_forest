package com.bureung.memoryforest.common.application;

import com.bureung.memoryforest.common.domain.FileInfo;

import org.springframework.web.multipart.MultipartFile;

public interface FileService {
    
    /**
     * S3에 파일 업로드
     */
    FileInfo uploadFileToS3(MultipartFile file);
    
    /**
     * 파일 ID로 파일 정보 조회
     */
    FileInfo getFileById(Integer fileId);
}
