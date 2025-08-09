package com.bureung.memoryforest.common.application;

import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

public interface S3Service {
    
    /**
     * 파일을 S3에 업로드
     */
    String uploadFile(MultipartFile file) throws IOException;
} 