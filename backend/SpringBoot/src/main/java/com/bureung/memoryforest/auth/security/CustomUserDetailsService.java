// package com.bureung.memoryforest.auth.security;

// import com.bureung.memoryforest.user.repository.UserRepository;
// import lombok.RequiredArgsConstructor;
// import org.springframework.security.core.userdetails.*;
// import org.springframework.stereotype.Service;

// @Service
// @RequiredArgsConstructor
// public class CustomUserDetailsService implements UserDetailsService {

//     private final UserRepository userRepository;

//     @Override
//     public UserDetails loadUserByUsername(String userId) throws UsernameNotFoundException {
//         return userRepository.findByUserId(userId)
//                 .map(CustomUserDetails::new)
//                 .orElseThrow(() -> new UsernameNotFoundException("사용자 없음"));
//     }
// }
