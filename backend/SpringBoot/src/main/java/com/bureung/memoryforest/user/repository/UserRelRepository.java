package com.bureung.memoryforest.user.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.bureung.memoryforest.user.domain.UserRel;
import com.bureung.memoryforest.user.domain.UserRelId;

@Repository
public interface UserRelRepository extends JpaRepository<UserRel, UserRelId> {
    List<UserRel> findByIdFamilyId(String familyId);

    List<UserRel> findByIdFamilyIdOrderByCreatedAtDesc(String familyId);
}
