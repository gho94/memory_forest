package com.bureung.memoryforest.user.repository;

import com.bureung.memoryforest.user.domain.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, String> {
    Optional<User> findByUserId(String userId);
    Optional<User> findByEmail(String email);
    Optional<User> findByUserIdAndEmail(String userId, String email);

    boolean existsByEmail(String email);
    boolean existsByUserId(String userId);

}
