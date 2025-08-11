package com.bureung.memoryforest.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserService;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;

import java.util.Arrays;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    //leb. 임시로 둔 것으로 추후 수정해야 함.
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        OAuth2UserService<OAuth2UserRequest, OAuth2User> customOAuth2UserService = null;
        AuthenticationSuccessHandler oAuth2LoginSuccessHandler = null;
        http
                .cors(cors -> cors.configurationSource(corsConfigurationSource()))
                .csrf(csrf -> csrf.disable())
//                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)) // 일단 1차로 기본 세션 관리만 설정 (JWT는 나중에 추가)
                .sessionManagement(session -> session
                        .maximumSessions(1)
                        .maxSessionsPreventsLogin(false)
                )
                .authorizeHttpRequests(auth -> auth
                                .requestMatchers( //공통 접근 허용된 경로들
                                        "/",
                                        "/api/auth/**",           // 로그인/회원가입/로그아웃 API
                                        "/api/auth/check/**",    // 중복체크 API
                                        "/findId",
                                        "/signup",
                                        "/welcome",
                                        "/findPw",
                                        "/static/**",             // React 정적 파일들
                                        "/assets/**",
                                        "/*.js",
                                        "/*.css",
                                        "/error",
                                        "/login/oauth2/code/**"
                                ).permitAll()

                                // 기록자(RECORDER) 전용 경로
                                .requestMatchers("/recorder", "/recorder/**")
//                        .hasRole("RECORDER")
                                .hasAuthority("ROLE_A20001")

//                         /* // 동행자(COMPANION) 전용 경로
//                         .requestMatchers("/companion", "/companion/**")
// //                        .hasRole("COMPANION")
//                         .hasAuthority("ROLE_A20002") */

//                        .anyRequest().permitAll()  // 모든 요청 허용
                        .anyRequest().authenticated()
                )
                .httpBasic(httpBasic -> httpBasic.disable())  // HTTP Basic 인증 비활성화
                .formLogin(form -> form.disable())  // 폼 로그인 비활성화
                .oauth2Login(oauth2 -> oauth2
                        .userInfoEndpoint(userInfo -> userInfo
                                .userService(customOAuth2UserService)
                        )
                        .successHandler(oAuth2LoginSuccessHandler)
                        .failureUrl("http://localhost:3000/?error=oauth")
                )
                .logout(logout -> logout.disable());  // 로그아웃 비활성화

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();

        // 허용할 Origin 설정
        configuration.setAllowedOriginPatterns(Arrays.asList("http://localhost:3000", "http://localhost:*"));

        // 허용할 HTTP 메서드
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"));

        // 허용할 헤더
        configuration.setAllowedHeaders(Arrays.asList("*"));

        // 인증 정보 포함 허용
        configuration.setAllowCredentials(true);

        // preflight 캐시 시간
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }
}