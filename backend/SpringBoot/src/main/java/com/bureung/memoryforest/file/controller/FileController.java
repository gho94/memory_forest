package com.bureung.memoryforest.file.controller;

import com.bureung.memoryforest.file.application.FileService;
import com.bureung.memoryforest.file.dto.request.FileUploadRequestDto;
import com.bureung.memoryforest.file.dto.response.FileUploadResponseDto;
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
    public ResponseEntity<FileUploadResponseDto> uploadFile(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "createdBy", required = false) String createdBy,
            @RequestParam(value = "isPublic", defaultValue = "false") String isPublic) {
        
        FileUploadRequestDto uploadRequest = FileUploadRequestDto.builder()
                .createdBy(createdBy)
                .isPublic(isPublic)
                .build();
        
        FileUploadResponseDto uploadedFile = fileService.uploadFileToS3(file, uploadRequest);
        return ResponseEntity.ok(uploadedFile);
    }

    /**
     * 파일 ID로 파일 정보 조회
     */
    @GetMapping("/{fileId}")
    public ResponseEntity<FileUploadResponseDto> getFileById(@PathVariable Integer fileId) {
        FileUploadResponseDto fileInfo = fileService.getFileById(fileId);
        if (fileInfo == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(fileInfo);
    }
} 