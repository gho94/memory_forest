package com.bureung.memoryforest.common.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import com.bureung.memoryforest.common.domain.CommonCode;

public interface CommonCodeRepository extends JpaRepository<CommonCode, String> {
    
    @Query(value = "SELECT c.code_id FROM common_codes c WHERE c.code_id LIKE :header% ORDER BY c.code_id DESC LIMIT 1", nativeQuery = true)
    String findLastCodeIdByHeader(@Param("header") String header);
    
    @Query(value = "SELECT c.code_id FROM common_codes c ORDER BY c.code_id DESC LIMIT 1", nativeQuery = true)
    String findLastCodeId();

    List<CommonCode> findByParentCodeIDOrderByCodeID(String parentCodeID);
}
