package com.bureung.memoryforest.record.domain;

import lombok.*;

import javax.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "records")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Record {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "record_id")
    private Integer recordId;

    @Column(name = "score")
    private Integer score;

    @Column(name = "user_id", length = 10)
    private String userId;

    @Column(name = "file_id")
    private Integer fileId;

    @Column(name = "text", columnDefinition = "LONGTEXT")
    private String text;

    @Column(name = "duration")
    private Integer duration;

    @Column(name = "created_at")
    private LocalDateTime createdAt;
}