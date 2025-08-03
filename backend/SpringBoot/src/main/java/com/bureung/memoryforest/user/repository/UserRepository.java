// package com.bureung.memoryforest.user.repository;

// public class UserRepository {
// }
package com.bureung.memoryforest.user.repository;

import com.bureung.memoryforest.user.domain.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, String> {
    Optional<User> findByUserId(String userId);
}
