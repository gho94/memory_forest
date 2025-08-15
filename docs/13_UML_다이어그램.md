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
        +Long id
        +String email
        +String name
        +String role
        +LocalDateTime createdAt
        +LocalDateTime updatedAt
        +createUser()
        +updateUser()
        +deleteUser()
    }

    class Patient {
        +Long id
        +Long userId
        +String name
        +int age
        +String gender
        +String diagnosis
        +LocalDateTime diagnosisDate
        +createPatient()
        +updatePatient()
    }

    class FamilyMember {
        +Long id
        +Long userId
        +Long patientId
        +String relationship
        +String phoneNumber
        +createFamilyMember()
        +updateFamilyMember()
    }

    class GameMaster {
        +Long id
        +Long patientId
        +String gameType
        +LocalDateTime startTime
        +LocalDateTime endTime
        +int totalScore
        +createGame()
        +endGame()
        +calculateScore()
    }

    class GameDetail {
        +Long id
        +Long gameMasterId
        +Long contentId
        +String question
        +String correctAnswer
        +String userAnswer
        +boolean isCorrect
        +int responseTime
        +int score
        +processAnswer()
        +calculateScore()
    }

    class Content {
        +Long id
        +Long userId
        +String fileName
        +String originalFileName
        +String filePath
        +String description
        +String category
        +LocalDateTime uploadDate
        +uploadContent()
        +updateContent()
        +deleteContent()
    }

    class AIAnalysis {
        +Long id
        +Long contentId
        +String analysisType
        +String keywords
        +String similarWords
        +double difficultyScore
        +LocalDateTime analysisDate
        +analyzeContent()
        +generateQuestions()
    }

    class Progress {
        +Long id
        +Long patientId
        +LocalDate date
        +int gamesPlayed
        +double averageScore
        +int totalPlayTime
        +updateProgress()
        +calculateTrends()
    }

    class Notification {
        +Long id
        +Long userId
        +String type
        +String message
        +boolean isRead
        +LocalDateTime createdAt
        +sendNotification()
        +markAsRead()
    }

    User ||--o{ Patient : manages
    User ||--o{ FamilyMember : has
    Patient ||--o{ GameMaster : plays
    GameMaster ||--o{ GameDetail : contains
    Content ||--o{ AIAnalysis : analyzed_by
    Patient ||--o{ Progress : tracks
    User ||--o{ Notification : receives
    FamilyMember ||--o{ Patient : cares_for
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
        +updateUserProfile(Long userId, UserUpdateDto updateDto)
        +deleteUser(Long userId)
    }

    class GameService {
        +GameMasterRepository gameMasterRepository
        +GameDetailRepository gameDetailRepository
        +ContentService contentService
        +AIService aiService
        +createGameSession(Long patientId, String gameType)
        +processGameAnswer(Long gameId, Long contentId, String answer)
        +endGameSession(Long gameId)
        +calculateGameScore(Long gameId)
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
    }

    class ProgressService {
        +ProgressRepository progressRepository
        +GameMasterRepository gameMasterRepository
        +calculateDailyProgress(Long patientId, LocalDate date)
        +generateWeeklyReport(Long patientId, LocalDate startDate)
        +generateMonthlyReport(Long patientId, int year, int month)
        +analyzeTrends(Long patientId, int days)
    }

    class NotificationService {
        +NotificationRepository notificationRepository
        +EmailService emailService
        +sendGameReminder(Long patientId)
        +sendProgressUpdate(Long familyMemberId, Long patientId)
        +sendAchievementNotification(Long patientId, String achievement)
    }

    UserService --> UserRepository
    GameService --> GameMasterRepository
    GameService --> GameDetailRepository
    GameService --> ContentService
    GameService --> AIService
    ContentService --> ContentRepository
    ContentService --> FileService
    ContentService --> AIService
    ProgressService --> ProgressRepository
    ProgressService --> GameMasterRepository
    NotificationService --> NotificationRepository
    NotificationService --> EmailService
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

---

## 📊 4. 상태 다이어그램

### **4.1 게임 세션 상태 다이어그램**

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

### **4.2 사용자 계정 상태 다이어그램**

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

---

## 🔗 5. 컴포넌트 다이어그램

### **5.1 시스템 컴포넌트 구조**

```mermaid
component
    component "Frontend (React)" {
        component "Game Components" as GC
        component "User Components" as UC
        component "Admin Components" as AC
        component "Common Components" as CC
    }
    
    component "Backend (Spring Boot)" {
        component "User Controller" as UController
        component "Game Controller" as GController
        component "Content Controller" as CController
        component "Admin Controller" as AController
    }
    
    component "AI Service (FastAPI)" {
        component "Image Analysis" as IA
        component "Text Analysis" as TA
        component "Word2Vec Model" as WV
    }
    
    component "Database" {
        component "MySQL" as DB
        component "Redis Cache" as Cache
    }
    
    component "External Services" {
        component "File Storage (S3)" as S3
        component "Email Service" as Email
    }
    
    Frontend --> Backend : HTTP/REST
    Backend --> AI Service : HTTP/REST
    Backend --> Database : JDBC/JPA
    Backend --> External Services : HTTP/API
    AI Service --> Database : Database Connection
```

---

## 📋 6. 배치 다이어그램

### **6.1 시스템 배치 구조**

```mermaid
deployment
    node "Client Browser" {
        component "React SPA" as React
    }
    
    node "Load Balancer" {
        component "Nginx" as LB
    }
    
    node "Web Server 1" {
        component "Spring Boot App" as App1
        component "JVM" as JVM1
    }
    
    node "Web Server 2" {
        component "Spring Boot App" as App2
        component "JVM" as JVM2
    }
    
    node "AI Server" {
        component "FastAPI App" as AI
        component "Python Runtime" as Python
    }
    
    node "Database Server" {
        component "MySQL" as MySQL
        component "Redis" as Redis
    }
    
    node "Storage Server" {
        component "AWS S3" as S3
    }
    
    React --> LB : HTTPS
    LB --> App1 : HTTP
    LB --> App2 : HTTP
    App1 --> AI : HTTP
    App2 --> AI : HTTP
    App1 --> MySQL : JDBC
    App2 --> MySQL : JDBC
    App1 --> Redis : Jedis
    App2 --> Redis : Jedis
    App1 --> S3 : AWS SDK
    App2 --> S3 : AWS SDK
    AI --> MySQL : SQLAlchemy
```

---

## 📊 7. 활동 다이어그램

### **7.1 게임 플레이 활동 흐름**

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

---

## 📋 8. UML 모델 검증

### **8.1 모델 검증 체크리스트**

- [ ] **구조적 일관성**: 클래스 간 관계가 논리적으로 일치하는가?
- [ ] **명명 규칙**: 모든 요소가 명명 규칙을 따르는가?
- [ ] **완전성**: 모든 주요 기능이 모델에 포함되어 있는가?
- [ ] **명확성**: 다이어그램이 이해하기 쉬운가?
- [ ] **확장성**: 향후 기능 추가를 고려한 설계인가?

### **8.2 모델 개선 방안**

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
