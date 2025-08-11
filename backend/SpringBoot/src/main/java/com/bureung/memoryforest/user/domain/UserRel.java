package com.bureung.memoryforest.user.domain;

import java.time.LocalDateTime;

import org.hibernate.annotations.CreationTimestamp;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EmbeddedId;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Builder;

@Entity
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserRel {
    @EmbeddedId
    private UserRelId id;

    @Column(name = "relationship_code", length = 6, nullable = false)
    private String relationshipCode;

    @Column(name = "status_code", length = 6, nullable = false)
    private String statusCode;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
}
