# 📊 **UML 다이어그램 (Unified Modeling Language)**

> **프로젝트명**: Memory Forest - AI 기반 치매 케어 인지 훈련 플랫폼
> 
> **작성일**: 2025.01.15
> 
> **작성자**: 시스템 아키텍트

---

## 📋 1. UML 개요

### **1.1 UML 정의**
UML(Unified Modeling Language)은 소프트웨어 시스템을 시각적으로 모델링하기 위한 표준화된 모델링 언어입니다.

### **1.2 UML 다이어그램 종류**
- **구조 다이어그램**: 클래스, 객체, 컴포넌트, 배치 다이어그램
- **행위 다이어그램**: 유스케이스, 활동, 상태, 시퀀스 다이어그램

---

## 🏗️ 2. 클래스 다이어그램

### **2.1 도메인 모델 클래스 다이어그램**

```mermaid
classDiagram
    class User {
        +String userId
        +String loginId
        +String userName
        +String password
        +String email
        +String phone
        +LocalDate birthDate
        +String genderCode
        +String userTypeCode
        +Integer profileImageFileId
        +String statusCode
        +String createdBy
        +LocalDateTime createdAt
        +String updatedBy
        +LocalDateTime updatedAt
        +LocalDateTime loginAt
        +String loginType
        +getAuthorities()
        +getUsername()
        +getPassword()
        +isAccountNonExpired()
        +isAccountNonLocked()
        +isCredentialsNonExpired()
        +isEnabled()
    }

    class GameMaster {
        +String gameId
        +String gameName
        +String gameDesc
        +Integer gameCount
        +String difficultyLevelCode
        +String creationStatusCode
        +String createdBy
        +LocalDateTime createdAt
        +String updatedBy
        +LocalDateTime updatedAt
    }

    class GameDetail {
        +String gameId
        +Integer gameSeq
        +Integer gameOrder
        +String gameTitle
        +String gameDesc
        +Integer fileId
        +String answerText
        +String wrongOption1
        +String wrongOption2
        +String wrongOption3
        +Double wrongScore1
        +Double wrongScore2
        +Double wrongScore3
        +String aiStatusCode
        +LocalDateTime aiProcessedAt
        +String description
    }

    class GamePlayer {
        +GamePlayerId id
        +Integer totalScore
        +Integer correctCount
        +BigDecimal accuracyRate
        +String gameStatusCode
        +LocalDateTime startTime
        +LocalDateTime endTime
        +Integer durationSeconds
    }

    class GamePlayerId {
        +String gameId
        +String playerId
    }

    class FileInfo {
        +Integer fileId
        +String originalName
        +String s3Key
        +String s3Url
        +String bucketName
        +Long fileSize
        +String contentType
        +LocalDateTime uploadDate
        +String createdBy
        +String isPublic
    }

    class CommonCode {
        +String codeID
        +String codeName
        +String parentCodeID
        +String useYn
        +String createdBy
        +LocalDateTime createdAt
        +String updatedBy
        +LocalDateTime updatedAt
    }

    class Record {
        +Integer recordId
        +Integer score
        +String userId
        +Integer fileId
        +String text
        +Integer duration
        +LocalDateTime createdAt
    }

    class Alarm {
        +Integer alarmId
        +GamePlayer game
        +String isRead
        +LocalDateTime createdAt
        +markAsRead()
    }

    class UserRel {
        +UserRelId id
        +String relationshipCode
        +String statusCode
        +LocalDateTime createdAt
    }

    class UserRelId {
        +String userId
        +String relatedUserId
    }

    User --> GameMaster
    User --> GamePlayer
    GameMaster --> GameDetail
    GameMaster --> GamePlayer
    User --> FileInfo
    User --> Record
    User --> Alarm
    User --> UserRel
    GameDetail --> FileInfo
```

### **2.2 서비스 레이어 클래스 다이어그램**

```mermaid
classDiagram
    class UserService {
        +UserRepository userRepository
        +PasswordEncoder passwordEncoder
        +JwtTokenProvider jwtTokenProvider
        +registerUser(UserDto userDto)
        +authenticateUser(LoginDto loginDto)
        +updateUserProfile(String userId, UserUpdateDto updateDto)
        +deleteUser(String userId)
    }

    class GameService {
        +GameMasterRepository gameMasterRepository
        +GameDetailRepository gameDetailRepository
        +GamePlayerRepository gamePlayerRepository
        +ContentService contentService
        +AIService aiService
        +createGameSession(String patientId, String gameType)
        +processGameAnswer(String gameId, Integer gameSeq, String answer)
        +endGameSession(String gameId)
        +calculateGameScore(String gameId)
    }

    class GameMasterService {
        +GameMasterRepository gameMasterRepository
        +GameDetailRepository gameDetailRepository
        +createGame(GameCreateRequestDto requestDto)
        +updateGameStatus(String gameId, String statusCode)
        +getGameDashboard(GameDashboardRequestDto requestDto)
    }

    class ContentService {
        +ContentRepository contentRepository
        +FileService fileService
        +AIService aiService
        +uploadContent(MultipartFile file, ContentDto contentDto)
        +analyzeContent(Long contentId)
        +getContentByCategory(String category)
        +deleteContent(Long contentId)
    }

    class AIService {
        +Word2VecModel word2VecModel
        +ImageAnalysisModel imageAnalysisModel
        +TextAnalysisModel textAnalysisModel
        +analyzeImage(MultipartFile image)
        +analyzeText(String text)
        +findSimilarWords(String word)
        +calculateDifficulty(String content)
        +generateWrongOptions(String answerText, String difficulty)
    }

    class ProgressService {
        +ProgressRepository progressRepository
        +GameMasterRepository gameMasterRepository
        +GamePlayerRepository gamePlayerRepository
        +calculateDailyProgress(String patientId, LocalDate date)
        +generateWeeklyReport(String patientId, LocalDate startDate)
        +generateMonthlyReport(String patientId, int year, int month)
        +analyzeTrends(String patientId, int days)
    }

    class NotificationService {
        +NotificationRepository notificationRepository
        +EmailService emailService
        +sendGameReminder(String patientId)
        +sendProgressUpdate(String familyMemberId, String patientId)
        +sendAchievementNotification(String patientId, String achievement)
    }

    class AuthService {
        +UserRepository userRepository
        +PasswordEncoder passwordEncoder
        +JwtTokenProvider jwtTokenProvider
        +EmailService emailService
        +login(String loginId, String password)
        +register(RegisterRequestDto requestDto)
        +verifyEmail(String email, String verificationCode)
        +sendVerificationEmail(String email)
    }

    class CustomOAuth2UserService {
        +UserRepository userRepository
        +loadUser(OAuth2UserRequest userRequest)
        +processOAuth2User(OAuth2User oauth2User, String provider)
    }

    UserService --> UserRepository
    GameService --> GameMasterRepository
    GameService --> GameDetailRepository
    GameService --> GamePlayerRepository
    GameService --> ContentService
    GameService --> AIService
    GameMasterService --> GameMasterRepository
    GameMasterService --> GameDetailRepository
    ContentService --> ContentRepository
    ContentService --> FileService
    ContentService --> AIService
    ProgressService --> ProgressRepository
    ProgressService --> GameMasterRepository
    ProgressService --> GamePlayerRepository
    NotificationService --> NotificationRepository
    NotificationService --> EmailService
    AuthService --> UserRepository
    AuthService --> PasswordEncoder
    AuthService --> JwtTokenProvider
    AuthService --> EmailService
    CustomOAuth2UserService --> UserRepository
```

---

## 🔄 3. 시퀀스 다이어그램

### **3.1 게임 플레이 시퀀스**

```mermaid
sequenceDiagram
    participant P as Patient
    participant F as Frontend
    participant B as Backend
    participant G as GameService
    participant A as AIService
    participant DB as Database

    P->>F: 게임 시작
    F->>B: POST /api/game/start
    B->>G: createGameSession()
    G->>DB: 저장된 콘텐츠 조회
    DB-->>G: 콘텐츠 목록 반환
    G->>A: AI 분석 결과 조회
    A-->>G: 분석 결과 반환
    G->>DB: 게임 세션 저장
    DB-->>G: 저장 완료
    G-->>B: 게임 세션 정보
    B-->>F: 게임 시작 응답
    F-->>P: 첫 번째 문제 표시

    loop 게임 진행
        P->>F: 답변 선택
        F->>B: POST /api/game/answer
        B->>G: processGameAnswer()
        G->>DB: 답변 결과 저장
        G->>G: 점수 계산
        G-->>B: 답변 결과
        B-->>F: 정답 여부 및 점수
        F-->>P: 결과 표시
        
        alt 마지막 문제
            F->>B: POST /api/game/end
            B->>G: endGameSession()
            G->>G: 최종 점수 계산
            G->>DB: 게임 결과 저장
            G-->>B: 최종 결과
            B-->>F: 게임 완료 응답
            F-->>P: 최종 결과 표시
        else 다음 문제
            F-->>P: 다음 문제 표시
        end
    end
```

### **3.2 콘텐츠 업로드 시퀀스**

```mermaid
sequenceDiagram
    participant F as FamilyMember
    participant FE as Frontend
    participant B as Backend
    participant C as ContentService
    participant FS as FileService
    participant A as AIService
    participant DB as Database

    F->>FE: 사진 업로드
    FE->>B: POST /api/content/upload
    B->>C: uploadContent()
    C->>FS: 파일 저장
    FS-->>C: 파일 경로 반환
    C->>DB: 콘텐츠 메타데이터 저장
    DB-->>C: 저장 완료
    C->>A: AI 분석 요청
    A->>A: 이미지 분석
    A->>A: 텍스트 분석
    A->>A: 유사도 계산
    A-->>C: 분석 결과
    C->>DB: AI 분석 결과 저장
    DB-->>C: 저장 완료
    C-->>B: 업로드 완료
    B-->>FE: 성공 응답
    FE-->>F: 업로드 완료 메시지
```

### **3.3 사용자 인증 시퀀스**

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant B as Backend
    participant US as UserService
    participant DB as Database
    participant JWT as JWTProvider

    U->>FE: 로그인 정보 입력
    FE->>B: POST /api/auth/login
    B->>US: authenticateUser()
    US->>DB: 사용자 정보 조회
    DB-->>US: 사용자 정보
    US->>US: 비밀번호 검증
    alt 인증 성공
        US->>JWT: 토큰 생성
        JWT-->>US: JWT 토큰
        US->>DB: 로그인 시간 업데이트
        DB-->>US: 업데이트 완료
        US-->>B: 인증 성공 + 토큰
        B-->>FE: 로그인 성공 + 토큰
        FE->>FE: 토큰 저장
        FE-->>U: 메인 페이지 이동
    else 인증 실패
        US-->>B: 인증 실패
        B-->>FE: 오류 메시지
        FE-->>U: 오류 메시지 표시
    end
```

### **3.4 AI 분석 시퀀스**

```mermaid
sequenceDiagram
    participant B as Backend
    participant AI as AIService
    participant F as FastAPI
    participant WV as Word2Vec
    participant DB as Database

    B->>AI: 분석 요청
    AI->>F: POST /analyze
    F->>WV: 모델 로드 확인
    WV-->>F: 모델 상태
    F->>F: 텍스트 전처리
    F->>WV: 키워드 추출
    WV-->>F: 키워드 목록
    F->>WV: 유사어 생성
    WV-->>F: 유사어 목록
    F->>F: 점수 계산
    F-->>AI: 분석 결과
    AI->>DB: 결과 저장
    DB-->>AI: 저장 완료
    AI-->>B: 분석 완료 응답
```

---

## 📊 4. 유스케이스 다이어그램

### **4.1 전체 시스템 유스케이스 다이어그램**

```mermaid
graph TB
    %% Actors
    Patient[환자]
    Family[가족 구성원]
    Admin[관리자]
    
    %% Use Cases
    UC1[회원가입/로그인]
    UC2[게임 플레이]
    UC3[진행도 확인]
    UC4[콘텐츠 업로드]
    UC5[AI 분석 요청]
    UC6[게임 생성/관리]
    UC7[사용자 관리]
    UC8[시스템 모니터링]
    UC9[데이터 백업]
    UC10[보고서 생성]
    
    %% Relationships
    Patient --> UC1
    Patient --> UC2
    Patient --> UC3
    
    Family --> UC1
    Family --> UC4
    Family --> UC5
    Family --> UC3
    
    Admin --> UC6
    Admin --> UC7
    Admin --> UC8
    Admin --> UC9
    Admin --> UC10
```

### **4.2 환자 유스케이스 상세**

```mermaid
graph TB
    %% Patient Actor
    Patient[환자]
    
    %% Patient Use Cases
    PUC1[계정 생성]
    PUC2[로그인]
    PUC3[게임 선택]
    PUC4[게임 플레이]
    PUC5[답변 제출]
    PUC6[결과 확인]
    PUC7[진행도 조회]
    PUC8[프로필 수정]
    PUC9[로그아웃]
    
    %% Relationships
    Patient --> PUC1
    Patient --> PUC2
    Patient --> PUC3
    Patient --> PUC4
    Patient --> PUC5
    Patient --> PUC6
    Patient --> PUC7
    Patient --> PUC8
    Patient --> PUC9
    
    %% Flow
    PUC1 --> PUC2
    PUC2 --> PUC3
    PUC3 --> PUC4
    PUC4 --> PUC5
    PUC5 --> PUC6
    PUC6 --> PUC7
```

### **4.3 가족 구성원 유스케이스 상세**

```mermaid
graph TB
    %% Family Actor
    Family[가족 구성원]
    
    %% Family Use Cases
    FUC1[계정 생성]
    FUC2[환자 연결]
    FUC3[콘텐츠 업로드]
    FUC4[AI 분석 요청]
    FUC5[진행도 모니터링]
    FUC6[게임 생성]
    FUC7[보고서 조회]
    FUC8[알림 설정]
    
    %% Relationships
    Family --> FUC1
    Family --> FUC2
    Family --> FUC3
    Family --> FUC4
    Family --> FUC5
    Family --> FUC6
    Family --> FUC7
    Family --> FUC8
    
    %% Flow
    FUC1 --> FUC2
    FUC2 --> FUC3
    FUC3 --> FUC4
    FUC4 --> FUC5
    FUC5 --> FUC6
    FUC6 --> FUC7
    FUC7 --> FUC8
```

### **4.4 관리자 유스케이스 상세**

```mermaid
graph TB
    %% Admin Actor
    Admin[관리자]
    
    %% Admin Use Cases
    AUC1[시스템 접근]
    AUC2[사용자 관리]
    AUC3[게임 콘텐츠 관리]
    AUC4[AI 모델 관리]
    AUC5[시스템 모니터링]
    AUC6[데이터 백업]
    AUC7[보고서 생성]
    AUC8[권한 관리]
    AUC9[시스템 설정]
    
    %% Relationships
    Admin --> AUC1
    Admin --> AUC2
    Admin --> AUC3
    Admin --> AUC4
    Admin --> AUC5
    Admin --> AUC6
    Admin --> AUC7
    Admin --> AUC8
    Admin --> AUC9
    
    %% Flow
    AUC1 --> AUC2
    AUC2 --> AUC3
    AUC3 --> AUC4
    AUC4 --> AUC5
    AUC5 --> AUC6
    AUC6 --> AUC7
    AUC7 --> AUC8
    AUC8 --> AUC9
```

---

## 📊 5. 상태 다이어그램

### **5.1 게임 세션 상태 다이어그램**

```mermaid
stateDiagram-v2
    [*] --> Created : 게임 세션 생성
    Created --> Ready : 초기화 완료
    Ready --> Playing : 게임 시작
    Playing --> QuestionDisplay : 문제 표시
    QuestionDisplay --> AnswerProcessing : 답변 처리
    AnswerProcessing --> ScoreCalculation : 점수 계산
    ScoreCalculation --> NextQuestion : 다음 문제
    
    NextQuestion --> QuestionDisplay : 문제가 남음
    NextQuestion --> GameComplete : 모든 문제 완료
    
    GameComplete --> [*] : 게임 종료
    
    Playing --> Paused : 일시정지
    Paused --> Playing : 재개
    Paused --> GameComplete : 강제 종료
```

### **5.2 사용자 계정 상태 다이어그램**

```mermaid
stateDiagram-v2
    [*] --> Guest : 방문자
    Guest --> Registered : 회원가입
    Registered --> Active : 이메일 인증
    Active --> Suspended : 정지
    Suspended --> Active : 정지 해제
    Active --> Inactive : 비활성화
    Inactive --> Active : 재활성화
    Active --> Deleted : 탈퇴
    Deleted --> [*] : 계정 삭제
```

### **5.3 AI 분석 상태 다이어그램**

```mermaid
stateDiagram-v2
    [*] --> Pending : 분석 대기
    Pending --> Processing : 분석 중
    Processing --> Completed : 분석 완료
    Processing --> Failed : 분석 실패
    Completed --> [*] : 결과 반환
    Failed --> [*] : 오류 처리
```

---

## 🔗 6. 컴포넌트 다이어그램

### **6.1 시스템 컴포넌트 구조**

```mermaid
graph TB
    %% Frontend Components
    GC[Game Components]
    UC[User Components]
    AC[Admin Components]
    CC[Common Components]
    CH[Chart Components]
    
    %% Backend Components
    UController[User Controller]
    GController[Game Controller]
    CController[Content Controller]
    AController[Admin Controller]
    AuthController[Auth Controller]
    
    %% AI Service Components
    IA[Image Analysis]
    TA[Text Analysis]
    WV[Word2Vec Model]
    KN[KoNLPy]
    
    %% Database Components
    DB[(MySQL 8.0)]
    Cache[(Redis 7.0)]
    
    %% External Services
    S3[File Storage S3]
    Email[Email Service]
    OAuth[OAuth2 Naver]
    
    %% Relationships
    GC --> UController
    UController --> IA
    UController --> DB
    UController --> S3
    IA --> DB
```

---

## 📋 7. 배치 다이어그램

### **7.1 시스템 배치 구조**

```mermaid
graph TB
    subgraph "Client Browser"
        React[React 19 SPA]
    end
    
    subgraph "Load Balancer"
        LB[Nginx]
    end
    
    subgraph "Web Server 1"
        App1[Spring Boot App]
        JVM1[JVM 21]
    end
    
    subgraph "Web Server 2"
        App2[Spring Boot App]
        JVM2[JVM 21]
    end
    
    subgraph "AI Server"
        AI[FastAPI App]
        Python[Python 3.10]
        Model[Word2Vec Model]
    end
    
    subgraph "Database Server"
        MySQL[(MySQL 8.0)]
        Redis[(Redis 7.0)]
    end
    
    subgraph "Storage Server"
        S3[AWS S3]
    end
    
    React --> LB
    LB --> App1
    LB --> App2
    App1 --> AI
    App2 --> AI
    App1 --> MySQL
    App2 --> MySQL
    App1 --> Redis
    App2 --> Redis
    App1 --> S3
    App2 --> S3
    AI --> MySQL
    AI --> Model
```

---

## 📊 8. 활동 다이어그램

### **8.1 게임 플레이 활동 흐름**

```mermaid
flowchart TD
    A[게임 시작] --> B[사용자 인증 확인]
    B --> C{인증 상태?}
    C -->|미인증| D[로그인 페이지로 이동]
    C -->|인증됨| E[게임 세션 생성]
    E --> F[콘텐츠 로드]
    F --> G[AI 분석 결과 조회]
    G --> H[첫 번째 문제 표시]
    H --> I[사용자 답변 대기]
    I --> J[답변 처리]
    J --> K[점수 계산]
    K --> L{마지막 문제?}
    L -->|아니오| M[다음 문제 표시]
    M --> I
    L -->|예| N[최종 점수 계산]
    N --> O[결과 저장]
    O --> P[진행도 업데이트]
    P --> Q[결과 화면 표시]
    Q --> R[게임 종료]
```

### **8.2 AI 분석 활동 흐름**

```mermaid
flowchart TD
    A[분석 요청] --> B[모델 로드 확인]
    B --> C{모델 상태?}
    C -->|로드됨| D[텍스트 전처리]
    C -->|로드 안됨| E[모델 로드]
    E --> D
    D --> F[형태소 분석]
    F --> G[키워드 추출]
    G --> H[Word2Vec 유사도 계산]
    H --> I[결과 정규화]
    I --> J[점수 변환]
    J --> K[결과 저장]
    K --> L[응답 반환]
```

---

## 📋 9. UML 모델 검증

### **9.1 모델 검증 체크리스트**

- [ ] **구조적 일관성**: 클래스 간 관계가 논리적으로 일치하는가?
- [ ] **명명 규칙**: 모든 요소가 명명 규칙을 따르는가?
- [ ] **완전성**: 모든 주요 기능이 모델에 포함되어 있는가?
- [ ] **명확성**: 다이어그램이 이해하기 쉬운가?
- [ ] **확장성**: 향후 기능 추가를 고려한 설계인가?

### **9.2 모델 개선 방안**

1. **성능 최적화**: 데이터베이스 쿼리 최적화를 위한 인덱스 설계
2. **보안 강화**: 인증/인가 로직의 세분화
3. **모니터링**: 시스템 상태 추적을 위한 로깅 구조
4. **확장성**: 마이크로서비스 아키텍처로의 전환 고려

---

**문서 정보**
- 작성일: 2025년 1월 15일
- 버전: v1.0
- 작성자: 시스템 아키텍트
- 검토자: 기술 책임자
- 승인자: CTO
