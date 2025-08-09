package com.bureung.memoryforest.common.application.impl;

import com.bureung.memoryforest.common.application.FileService;
import com.bureung.memoryforest.common.application.S3Service;
import com.bureung.memoryforest.common.domain.FileInfo;
import com.bureung.memoryforest.common.dto.request.FileUploadRequestDto;
import com.bureung.memoryforest.common.dto.response.FileUploadResponseDto;
import com.bureung.memoryforest.common.repository.FileRepository;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.time.LocalDateTime;
import java.time.ZoneId;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class FileServiceImpl implements FileService {

    private final FileRepository fileRepository;
    private final S3Service s3Service;

    @Override
    @Transactional
    public FileUploadResponseDto uploadFileToS3(MultipartFile file, FileUploadRequestDto uploadRequest) {
        try {
            // S3에 파일 업로드
            String fileUrl = s3Service.uploadFile(file);
            
            // 파일명에서 S3 키 추출 (URL에서 파일명 부분만)
            String fileName = fileUrl.substring(fileUrl.lastIndexOf("/") + 1);
            
            LocalDateTime kstNow = LocalDateTime.now(ZoneId.of("Asia/Seoul"));
            
            // isPublic 값을 Y/N으로 변환
            String isPublicValue = "false".equals(uploadRequest.getIsPublic()) ? "N" : "Y";
            
            // 데이터베이스에 파일 정보 저장
            FileInfo fileInfo = FileInfo.builder()
                    .originalName(file.getOriginalFilename())
                    .s3Key(fileName)
                    .s3Url(fileUrl)
                    .bucketName("memory-forest-test")
                    .fileSize(file.getSize())
                    .contentType(file.getContentType())
                    .uploadDate(kstNow)
                    .createdBy(uploadRequest.getCreatedBy())
                    .isPublic(isPublicValue)
                    .build();
            
            FileInfo savedFileInfo = fileRepository.save(fileInfo);
            
            return FileUploadResponseDto.builder()
                    .fileId(savedFileInfo.getFileID())
                    .originalName(savedFileInfo.getOriginalName())
                    .fileUrl(fileUrl)
                    .contentType(savedFileInfo.getContentType())
                    .fileSize(savedFileInfo.getFileSize())
                    .createdBy(savedFileInfo.getCreatedBy())
                    .uploadDate(savedFileInfo.getUploadDate().toString())
                    .build();
                    
        } catch (IOException e) {
            throw new RuntimeException("파일 업로드 중 오류가 발생했습니다.", e);
        }
    }

    @Override
    public FileUploadResponseDto getFileById(Integer fileId) {
        FileInfo fileInfo = fileRepository.findById(fileId).orElse(null);
        if (fileInfo == null) {
            return null;
        }
        
        return FileUploadResponseDto.builder()
                .fileId(fileInfo.getFileID())
                .originalName(fileInfo.getOriginalName())
                .fileUrl(fileInfo.getS3Url())
                .contentType(fileInfo.getContentType())
                .fileSize(fileInfo.getFileSize())
                .createdBy(fileInfo.getCreatedBy())
                .uploadDate(fileInfo.getUploadDate().toString())
                .build();
    }
}
