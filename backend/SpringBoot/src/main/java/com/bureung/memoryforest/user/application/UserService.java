package com.bureung.memoryforest.user.application;

import com.bureung.memoryforest.user.domain.User;
import com.bureung.memoryforest.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    public Optional<User> findByUserId(String userId) {
        return userRepository.findByUserId(userId);
    }

    public Optional<User> findByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    public Optional<User> findByUserIdAndEmail(String userId, String email) {
        return userRepository.findByUserIdAndEmail(userId, email);
    }

    //중복 체크
    public boolean existsByUserId(String userId) {
        return userRepository.existsByUserId(userId);
    }

    public boolean existsByEmail(String email) {
        return userRepository.existsByEmail(email);
    }

    //신규 user 생성
    public User createUser(String userId, String userName, String encodedPassword,
                           String email, String phone, String userTypeCode) {

        // 전화번호 입력 안받아서..
        if (phone == null || phone.trim().isEmpty()) {
            phone = "";
        }

        // userTypeCode 기본값 A20002
        if (userTypeCode == null || userTypeCode.trim().isEmpty()) {
            userTypeCode = "A20002";
        }

        User newUser = User.builder()
                .userId(userId)
                .userName(userName)
                .password(encodedPassword) // 이미 암호화된 상태로 받음
                .email(email)
                .phone(phone)
                .userTypeCode(userTypeCode)
                .statusCode("A20005") // 활성 상태
                .createdBy(userId)
                .createdAt(LocalDateTime.now())
                .build();

        return userRepository.save(newUser);
    }

    public User updateLoginTime(String userId) {
        Optional<User> userOptional = userRepository.findByUserId(userId);

        if (userOptional.isPresent()) {
            User user = userOptional.get();
            user.setLoginAt(LocalDateTime.now());
            return userRepository.save(user);
        }

        return null;
    }

    public User saveUser(User user) {
        return userRepository.save(user);
    }
}
