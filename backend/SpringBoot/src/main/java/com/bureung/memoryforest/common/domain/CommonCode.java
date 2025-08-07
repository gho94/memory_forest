package com.bureung.memoryforest.common.domain;

import java.time.LocalDateTime;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
@Entity
@Table(name = "common_codes")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CommonCode {
    @Id
    @Column(name = "code_id")
    private String codeID;

    @Column(name = "code_name", nullable = false, length = 100)
    private String codeName;

    @Column(name = "parent_code_id", nullable = true, length = 6)
    private String parentCodeID;

    @Column(name = "use_yn", nullable = false, length = 1)
    private String useYn;

    @Column(name = "created_by", nullable = false, length = 10)
    private String createdBy;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_by", nullable = true, length = 10)
    private String updatedBy;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = true)
    private LocalDateTime updatedAt;
}
