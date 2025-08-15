package com.bureung.memoryforest.user.repository;

import com.bureung.memoryforest.user.domain.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, String> {
    Optional<User> findByUserId(String userId);
    @Query("SELECT u FROM User u WHERE u.userId = :userId AND u.statusCode != 'A20008'")
    Optional<User> findByUserIdAndNotDeleted(String userId);
    Optional<User> findByLoginId(String loginId);
    Optional<User> findByEmail(String email);
    Optional<User> findByUserIdAndEmail(String userId, String email); //kys rollback
    Optional<User> findTopByOrderByUserIdDesc();

    boolean existsByEmail(String email);
    boolean existsByUserId(String userId);
    boolean existsByLoginId(String loginId);

    Optional<User> findByLoginTypeAndLoginId(String loginType, String socialId);
    boolean existsByLoginTypeAndLoginId(String loginType, String socialId);

    Optional<User> findByLoginIdAndEmail(String loginId, String email);

}
