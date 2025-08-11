package com.bureung.memoryforest.user.domain;

import java.io.Serializable;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Embeddable
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class UserRelId implements Serializable {
    @Column(name = "patient_id", length = 10, nullable = false)
    private String patientId;

    @Column(name = "family_id", length = 10, nullable = false)
    private String familyId;
}
