package com.bureung.memoryforest.file.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.bureung.memoryforest.file.domain.FileInfo;

public interface FileRepository extends JpaRepository<FileInfo, Integer> {

}
