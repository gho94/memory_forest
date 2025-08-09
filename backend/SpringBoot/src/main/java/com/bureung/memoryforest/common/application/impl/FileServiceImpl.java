package com.bureung.memoryforest.common.application.impl;

import com.bureung.memoryforest.common.application.FileService;
import com.bureung.memoryforest.common.application.S3Service;
import com.bureung.memoryforest.common.domain.FileInfo;
import com.bureung.memoryforest.common.repository.FileRepository;

import lombok.RequiredArgsConstructor;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class FileServiceImpl implements FileService {

    private final FileRepository fileRepository;
    private final S3Service s3Service;
    
    @Value("${aws.s3.bucket-name}")
    private String bucketName;

    @Override
    @Transactional
        public FileInfo uploadFileToS3(MultipartFile file) {
        try {
            String fileUrl = s3Service.uploadFile(file);            
            String fileName = fileUrl.substring(fileUrl.lastIndexOf("/") + 1);
                        
            FileInfo fileInfo = FileInfo.builder()
                    .originalName(file.getOriginalFilename())
                    .s3Key(fileName)
                    .s3Url(fileUrl)
                    .bucketName(bucketName)
                    .fileSize(file.getSize())
                    .contentType(file.getContentType())
                    .createdBy("ADMIN") //Todo 로그인 사용자 정보 추가
                    .isPublic("N")
                    .build();
            
            return fileRepository.save(fileInfo);
                    
        } catch (IOException e) {
            throw new RuntimeException("파일 업로드 중 오류가 발생했습니다.", e);
        }
    }

    @Override
    public FileInfo getFileById(Integer fileId) {
        FileInfo fileInfo = fileRepository.findById(fileId).orElse(null);
        if (fileInfo == null) {
            return null;
        }        
        return fileInfo;
    }
}
