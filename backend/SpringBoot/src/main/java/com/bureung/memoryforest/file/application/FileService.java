package com.bureung.memoryforest.file.application;

import com.bureung.memoryforest.file.dto.request.FileUploadRequestDto;
import com.bureung.memoryforest.file.dto.response.FileUploadResponseDto;
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
