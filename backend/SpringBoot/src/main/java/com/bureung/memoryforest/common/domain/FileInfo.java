package com.bureung.memoryforest.common.domain;

import lombok.*;
import jakarta.persistence.*;
import java.time.LocalDateTime;
import org.hibernate.annotations.CreationTimestamp;

@Entity
@Table(name = "file_info")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FileInfo {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "file_id")
    private Integer fileId;    

    @Column(name = "original_name", nullable = false, length = 255) 
    private String originalName;

    @Column(name = "s3_key", nullable = false, length = 255)
    private String s3Key;

    @Column(name = "s3_url", nullable = false, length = 255)
    private String s3Url;

    @Column(name = "bucket_name", nullable = false, length = 255)
    private String bucketName;

    @Column(name = "file_size", nullable = true)
    private Long fileSize;

    @Column(name = "content_type", nullable = true, length = 100)
    private String contentType;

    @CreationTimestamp
    @Column(name = "upload_date", nullable = false)
    private LocalDateTime uploadDate;

    @Column(name = "created_by", nullable = true, length = 10)
    private String createdBy;

    @Column(name = "is_public", nullable = false, length = 1)
    private String isPublic;
}