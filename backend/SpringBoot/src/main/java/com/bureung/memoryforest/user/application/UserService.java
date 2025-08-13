package com.bureung.memoryforest.user.application;

import com.bureung.memoryforest.user.domain.User;
import com.bureung.memoryforest.user.domain.UserRel;
import com.bureung.memoryforest.user.domain.UserRelId;
import com.bureung.memoryforest.user.dto.request.RecorderCreateDto;
import com.bureung.memoryforest.user.dto.response.RecorderListResponseDto;
import com.bureung.memoryforest.user.repository.UserRepository;
import com.bureung.memoryforest.user.repository.UserRelRepository;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final UserRelRepository userRelRepository;

    public Optional<User> findByUserId(String userId) {
        return userRepository.findByUserId(userId);
    }

    public Optional<User> findByLoginId(String loginId) {
        return userRepository.findByLoginId(loginId);
    }

    public Optional<User> findByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    //중복 체크
    public boolean existsByUserId(String userId) {
        return userRepository.existsByUserId(userId);
    }

    public boolean existsByLoginId(String loginId) {
        return userRepository.existsByLoginId(loginId);
    }

    public boolean existsByEmail(String email) {
        return userRepository.existsByEmail(email);
    }

    // 다음 userId 생성 (U0001, U0002, ...)
    private String generateNextUserId() {
        Optional<User> lastUser = userRepository.findTopByOrderByUserIdDesc();
        if (lastUser.isEmpty()) {
            return "U0001";
        }

        String lastUserId = lastUser.get().getUserId();
        if (lastUserId.startsWith("U")) {
            try {
                int number = Integer.parseInt(lastUserId.substring(1));
                return String.format("U%04d", number + 1);
            } catch (NumberFormatException e) {
                // 파싱 실패 시 기본값 반환
                return "U0001";
            }
        }
        return "U0001";
    }


    public Optional<User> findByLoginTypeAndLoginId(String loginType, String loginId) {
        return userRepository.findByLoginTypeAndLoginId(loginType, loginId);
    }

    public boolean existsByLoginTypeAndLoginId(String loginType, String loginId) {
        return userRepository.existsByLoginTypeAndLoginId(loginType, loginId);
    }

    //신규 user 생성
    public User createUser(String loginId, String userName, String encodedPassword,
                           String email, String phone, String userTypeCode, LocalDate birthDate, String genderCode) {

        // 전화번호 입력 안받아서..없앨까 ?
        if (phone == null || phone.trim().isEmpty()) {
            phone = "";
        }

        // userTypeCode 기본값 A20002
        if (userTypeCode == null || userTypeCode.trim().isEmpty()) {
            userTypeCode = "A20002";
        }

        // userId 자동 생성
        String userId = generateNextUserId();

        if (email == null || email.trim().isEmpty()) {
            //recorder 이메일이 없음
            email = userId + "@memoryforest.com";
        }

        User newUser = User.builder()
                .userId(userId)
                .loginId(loginId)
                .userName(userName)
                .password(encodedPassword) // 이미 암호화된 상태로 받음
                .email(email)
                .phone(phone)
                .birthDate(birthDate)
                .genderCode(genderCode)
                .userTypeCode(userTypeCode)
                .loginType ("DEFAULT")
                .statusCode("A20005") // 활성 상태
                .createdBy(userId)
                .createdAt(LocalDateTime.now())
                .build();

        return userRepository.save(newUser);
    }

    public User createRecorderUser(RecorderCreateDto requestDto) {
        String loginId = requestDto.getLoginId(); // userId가 아닌 loginId 사용
        String userName = requestDto.getUserName();
        String password = "jwt"; //TODO 토큰사용 예정
        String email = "";
        String phone = "";
        LocalDate birthDate = LocalDate.parse(requestDto.getBirthDate());
        String relationshipCode = requestDto.getRelationshipCode();
        String genderCode = requestDto.getGenderCode();
        String userTypeCode = requestDto.getUserTypeCode();

        User user = createUser(loginId, userName, password, email, phone, userTypeCode, birthDate, genderCode);
        UserRel userRel = UserRel.builder()
                .id(new UserRelId(user.getUserId(), requestDto.getLoginId()))    // userId 대신 loginId 사용
                .relationshipCode(relationshipCode)
                .statusCode("A20005") // 활성 상태
                .createdAt(LocalDateTime.now())
                .build();
        userRelRepository.save(userRel);
        return user;
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



    //소셜로그인
    public User createOAuthUser(String userName,String email,String phone,String loginType,String loginId, String userTypeCode) {

        if (phone == null || phone.trim().isEmpty()) {
            phone = "";
        }

        if (userTypeCode == null || userTypeCode.trim().isEmpty()) {
            userTypeCode = "A20002";
        }

        // userId 자동 생성
        String userId = generateNextUserId();

        User newUser = User.builder()
                .userId(userId)
                .loginId(loginId)
                .userName(userName)
                .password(null) // OAuth 사용자는 비밀번호 없음
                .email(email)
                .phone(phone)
                .userTypeCode(userTypeCode)
                .loginType (loginType)
                .statusCode("A20005")
                .createdBy("SYSTEM")
                .createdAt(LocalDateTime.now())
                .build();

        return userRepository.save(newUser);
    }

    // OAuth 사용자 정보 업데이트
    public User updateOAuthUser(User existingUser, String userName, String email, String phone) {
        existingUser.setUserName(userName);
        existingUser.setEmail(email);
        if (phone != null && !phone.trim().isEmpty()) {
            existingUser.setPhone(phone);
        }
        existingUser.setUpdatedAt(LocalDateTime.now());
        existingUser.setUpdatedBy("SYSTEM");

        return userRepository.save(existingUser);
    }

    public Optional<User> findByLoginIdAndEmail(String loginId, String email) {
        return userRepository.findByLoginIdAndEmail(loginId, email);
    }

    public List<RecorderListResponseDto> getRecorderList(String userId) {
        List<UserRel> userRelList = userRelRepository.findByIdFamilyId(userId);
        List<RecorderListResponseDto> recorderList = new ArrayList<>();
        for (UserRel userRel : userRelList) {
            Optional<User> userOpt = userRepository.findByUserId(userRel.getId().getPatientId());
            if (userOpt.isPresent()) {
                RecorderListResponseDto dto = RecorderListResponseDto.from(
                    userOpt.get(),
                    userRel.getRelationshipCode()
                );
                recorderList.add(dto);
            }
        }
        return recorderList;
    }
}
