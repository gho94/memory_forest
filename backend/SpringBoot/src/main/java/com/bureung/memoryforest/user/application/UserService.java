package com.bureung.memoryforest.user.application;

import com.bureung.memoryforest.user.domain.User;
import com.bureung.memoryforest.user.domain.UserRel;
import com.bureung.memoryforest.user.domain.UserRelId;
import com.bureung.memoryforest.user.dto.request.RecorderCreateDto;
import com.bureung.memoryforest.user.dto.request.RecorderUpdateDto;
import com.bureung.memoryforest.user.dto.response.RecorderListResponseDto;
import com.bureung.memoryforest.user.dto.response.UserRecorderResponseDto;
import com.bureung.memoryforest.user.repository.UserRepository;
import com.bureung.memoryforest.user.repository.UserRelRepository;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;


public interface UserService {
    Optional<User> findByUserId(String userId);
    Optional<User> findByLoginId(String loginId);
    Optional<User> findByEmail(String email);
    boolean existsByUserId(String userId);
    boolean existsByLoginId(String loginId);
    boolean existsByEmail(String email);
    Optional<User> findByLoginTypeAndLoginId(String loginType, String loginId);
    boolean existsByLoginTypeAndLoginId(String loginType, String loginId);
    User createUser(String loginId, String userName, String encodedPassword,
                    String email, String phone, String userTypeCode, LocalDate birthDate, String genderCode);
    User createRecorderUser(RecorderCreateDto requestDto);
    User createUser(String loginId, String userName, String encodedPassword,
                    String email, String phone, String userTypeCode, LocalDate birthDate, String genderCode, Integer fileId);
    User updateRecorderUser(RecorderUpdateDto requestDto);
    void deleteUserByFamilyId(String userId);
    User updateLoginTime(String userId);
    User saveUser(User user);
    User createOAuthUser(String userName,String email,String phone,String loginType,String loginId, String userTypeCode);
    User updateOAuthUser(User existingUser, String userName, String email, String phone);
    Optional<User> findByLoginIdAndEmail(String loginId, String email);
    List<RecorderListResponseDto> getRecorderList(String userId);
    UserRecorderResponseDto getRecorderInfo(String userId);

}
