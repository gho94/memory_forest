package com.bureung.memoryforest.common.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FileUploadResponseDto {
    private Integer fileId;
    private String originalName;
    private String fileName;
    private String fileUrl;
    private String contentType;
    private Long fileSize;
    private String createdBy;
    private String isPublic;
    private String description;
    private String uploadDate;
} 