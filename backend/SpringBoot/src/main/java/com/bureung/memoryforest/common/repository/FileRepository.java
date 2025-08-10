package com.bureung.memoryforest.common.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.bureung.memoryforest.common.domain.FileInfo;

public interface FileRepository extends JpaRepository<FileInfo, Integer> {

}
