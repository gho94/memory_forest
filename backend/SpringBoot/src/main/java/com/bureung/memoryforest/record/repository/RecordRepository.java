package com.bureung.memoryforest.record.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import com.bureung.memoryforest.record.domain.Record;

@Repository
public interface RecordRepository extends JpaRepository<Record, Integer> {
}
