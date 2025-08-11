package com.bureung.memoryforest.auth.application;

import com.bureung.memoryforest.auth.dto.request.JoinRequestDto;
import com.bureung.memoryforest.auth.dto.response.LoginResponseDto;
import com.bureung.memoryforest.auth.dto.response.JoinResponseDto;
import com.bureung.memoryforest.user.application.UserService;
import com.bureung.memoryforest.user.domain.User;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class AuthService implements UserDetailsService {

    private final UserService userService;
    private final PasswordEncoder passwordEncoder;
    private final EmailService emailService;

    @Override
    public UserDetails loadUserByUsername(String loginId) throws UsernameNotFoundException {
        return userService.findByLoginId(loginId)
                .orElseThrow(() -> new UsernameNotFoundException("사용자를 찾을 수 없습니다: " + loginId));
    }

    //로그인
    public LoginResponseDto login(String loginId, String password) {
        try {
            Optional<User> userOpt = userService.findByLoginId(loginId);

            if (userOpt.isEmpty()) {
                return LoginResponseDto.failure("사용자를 찾을 수 없습니다.");
            }

            User user = userOpt.get();

            if (!passwordEncoder.matches(password, user.getPassword())) {
                return LoginResponseDto.failure("비밀번호가 일치하지 않습니다.");
            }

            if (!"A20005".equals(user.getStatusCode())) {
                return LoginResponseDto.failure("비활성화된 계정입니다.");
            }

            userService.updateLoginTime(user.getUserId());
            return LoginResponseDto.success(user);

        } catch (Exception e) {
            return LoginResponseDto.failure("로그인 중 오류가 발생했습니다.");
        }
    }

    //뢰원가입
    public JoinResponseDto signup(JoinRequestDto request) {
        return signup(request, true);
    }

    //회원가입시 이메일 인증하기
    public JoinResponseDto signupWithoutEmailCheck(JoinRequestDto request) {
        return signup(request, false);
    }

    private JoinResponseDto signup(JoinRequestDto request, boolean checkEmailVerification) {
        try {
            // 이메일 인증 체크 (필요한 경우에만)
            if (checkEmailVerification && !emailService.isEmailVerified(request.getEmail())) {
                return JoinResponseDto.failure("이메일 인증이 필요합니다.");
            }

            // 중복 체크
            if (userService.existsByLoginId(request.getLoginId())) {
                return JoinResponseDto.failure("이미 존재하는 사용자 ID입니다.");
            }

            if (userService.existsByEmail(request.getEmail())) {
                return JoinResponseDto.failure("이미 사용중인 이메일입니다.");
            }

            userService.createUser(
                    request.getLoginId(),
                    request.getUserName(),
                    passwordEncoder.encode(request.getPassword()),
                    request.getEmail(),
                    request.getPhone(),
                    request.getUserTypeCode(),
                    null,
                    null
            );

            return JoinResponseDto.success("회원가입이 완료되었습니다.");

        } catch (Exception e) {
            return JoinResponseDto.failure("회원가입 중 오류가 발생했습니다.");
        }
    }


    //비밀번호 찾기를 네이버 비밀번호 찾기 흐름 맞춰서 비밀번호 재설정으로 구현했음
    public boolean updatePassword(String userId, String newPassword) {
        try {
            Optional<User> userOptional = userService.findByUserId(userId);

            if (userOptional.isEmpty()) {
                log.error("비밀번호 업데이트 실패: 사용자 없음 - {}", userId);
                return false;
            }

            User user = userOptional.get();
            user.setPassword(passwordEncoder.encode(newPassword));
            user.setUpdatedBy(userId);
            user.setUpdatedAt(LocalDateTime.now());

            userService.saveUser(user);
            log.info("비밀번호 업데이트 성공: {}", userId);
            return true;

        } catch (Exception e) {
            log.error("비밀번호 업데이트 중 오류 발생: {}", userId, e);
            return false;
        }
    }

    public Optional<User> findByUserId(String userId) {
        return userService.findByUserId(userId);
    }

    public Optional<User> findByEmail(String email) {
        return userService.findByEmail(email);
    }

    public Optional<User> findByUserIdAndEmail(String userId, String email) {
        return userService.findByUserIdAndEmail(userId, email);
    }

    //회원가입할때 이미 회원가입 이력이 존재하는 이메일인지 확인해야하는 로직 추가함
    public boolean existsByEmail(String email) {
        return userService.existsByEmail(email);
    }

    public boolean existsByLoginId(String loginId) {
        return userService.existsByLoginId(loginId);
    }


}