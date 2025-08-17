package com.bureung.memoryforest.user.repository;

import com.bureung.memoryforest.user.domain.User;
import com.bureung.memoryforest.user.dto.response.UserRecorderResponseDto;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
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

    @Query(value = """
    SELECT r.user_name as userName, r.gender_code as genderCode, DATE_FORMAT(r.birth_date, '%Y-%m-%d') as birthDate, 
           p.user_name as companionName, p.phone as companionPhone, ur.relationship_code as relationshipCode
    FROM users r 
    INNER JOIN user_rel ur ON r.user_id = ur.patient_id
    INNER JOIN users p ON p.user_id = ur.family_id
    WHERE r.user_id = :userId
    """, nativeQuery = true)
    UserRecorderResponseDto findRecorderInfo(@Param("userId") String userId);
}
