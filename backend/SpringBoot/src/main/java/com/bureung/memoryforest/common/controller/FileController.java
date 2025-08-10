package com.bureung.memoryforest.common.controller;

import com.bureung.memoryforest.common.application.FileService;
import com.bureung.memoryforest.common.domain.FileInfo;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/files")
@RequiredArgsConstructor
public class FileController {

    private final FileService fileService;

    /**
     * S3에 파일 업로드
     */
    @PostMapping("/upload")
    public ResponseEntity<FileInfo> uploadFile(@RequestParam("file") MultipartFile file) {
        FileInfo uploadedFile = fileService.uploadFileToS3(file);
        return ResponseEntity.ok(uploadedFile);
    }

    /**
     * 파일 ID로 파일 정보 조회
     */
    @GetMapping("/{fileId}")
    public ResponseEntity<FileInfo> getFileById(@PathVariable("fileId") Integer fileId) {
        FileInfo fileInfo = fileService.getFileById(fileId);
        if (fileInfo == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(fileInfo);
    }
} 