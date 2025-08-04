package com.bureung.memoryforest.file.dto.request;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FileUploadRequestDto {
    private String createdBy;
    private String isPublic;
} 