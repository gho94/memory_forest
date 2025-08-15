# 📄 **API 명세서 (API Specification)**

> **프로젝트명**: Memory Forest - AI 기반 치매 케어 인지 훈련 플랫폼
> 
> **작성일**: 2025.01.15
> 
> **작성자**: 백엔드 개발자

---

## 📋 1. API 개요

### **1.1 기본 정보**
- **Base URL**: `http://localhost:8080/api/v1`
- **인증 방식**: JWT Bearer Token
- **응답 형식**: JSON
- **문자 인코딩**: UTF-8

### **1.2 공통 응답 형식**

#### **성공 응답**
```json
{
  "success": true,
  "data": {},
  "message": "요청이 성공적으로 처리되었습니다.",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

#### **에러 응답**
```json
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "사용자를 찾을 수 없습니다.",
    "details": "요청한 사용자 ID가 존재하지 않습니다."
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### **1.3 HTTP 상태 코드**
- **200**: 성공
- **201**: 생성됨
- **400**: 잘못된 요청
- **401**: 인증 실패
- **403**: 권한 없음
- **404**: 리소스 없음
- **500**: 서버 내부 오류

---

## 🔐 2. 인증 관련 API

### **2.1 회원가입**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 회원가입 |
| **Method** | POST |
| **URL** | `/auth/register` |
| **설명** | 이메일과 비밀번호를 사용하여 새 계정을 생성합니다. |

#### **요청 파라미터**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "홍길동",
  "phone": "010-1234-5678"
}
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "userId": 123,
    "email": "user@example.com",
    "name": "홍길동",
    "status": "PENDING_VERIFICATION"
  },
  "message": "회원가입이 완료되었습니다. 이메일 인증을 진행해주세요."
}
```

### **2.2 이메일 인증**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 이메일 인증 |
| **Method** | POST |
| **URL** | `/auth/verify-email` |
| **설명** | 이메일로 전송된 인증 코드를 확인합니다. |

#### **요청 파라미터**
```json
{
  "email": "user@example.com",
  "verificationCode": "123456"
}
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "userId": 123,
    "emailVerified": true
  },
  "message": "이메일 인증이 완료되었습니다."
}
```

### **2.3 로그인**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 로그인 |
| **Method** | POST |
| **URL** | `/auth/login` |
| **설명** | 이메일과 비밀번호로 로그인하여 JWT 토큰을 발급받습니다. |

#### **요청 파라미터**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600,
    "user": {
      "id": 123,
      "email": "user@example.com",
      "name": "홍길동",
      "role": "USER"
    }
  },
  "message": "로그인이 성공했습니다."
}
```

### **2.4 OAuth2 로그인 (Naver)**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | Naver OAuth2 로그인 |
| **Method** | GET |
| **URL** | `/auth/oauth2/naver` |
| **설명** | Naver OAuth2를 통해 로그인합니다. |

#### **요청 파라미터**
```
?code={authorization_code}&state={state}
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600,
    "user": {
      "id": 123,
      "email": "user@naver.com",
      "name": "홍길동",
      "role": "USER"
    }
  },
  "message": "OAuth2 로그인이 성공했습니다."
}
```

### **2.5 토큰 갱신**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 토큰 갱신 |
| **Method** | POST |
| **URL** | `/auth/refresh` |
| **설명** | 리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다. |

#### **요청 파라미터**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600
  },
  "message": "토큰이 갱신되었습니다."
}
```

---

## 👤 3. 사용자 관리 API

### **3.1 사용자 프로필 조회**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 사용자 프로필 조회 |
| **Method** | GET |
| **URL** | `/users/profile` |
| **인증** | Bearer Token 필요 |
| **설명** | 현재 로그인한 사용자의 프로필 정보를 조회합니다. |

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "email": "user@example.com",
    "name": "홍길동",
    "phone": "010-1234-5678",
    "role": "USER",
    "status": "ACTIVE",
    "emailVerified": true,
    "profileImageUrl": "https://s3.amazonaws.com/profile/123.jpg",
    "createdAt": "2025-01-15T10:30:00Z",
    "updatedAt": "2025-01-15T10:30:00Z"
  }
}
```

### **3.2 사용자 프로필 수정**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 사용자 프로필 수정 |
| **Method** | PUT |
| **URL** | `/users/profile` |
| **인증** | Bearer Token 필요 |
| **설명** | 사용자의 프로필 정보를 수정합니다. |

#### **요청 파라미터**
```json
{
  "name": "홍길동",
  "phone": "010-9876-5432"
}
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "홍길동",
    "phone": "010-9876-5432",
    "updatedAt": "2025-01-15T11:00:00Z"
  },
  "message": "프로필이 성공적으로 수정되었습니다."
}
```

### **3.3 비밀번호 변경**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 비밀번호 변경 |
| **Method** | PUT |
| **URL** | `/users/change-password` |
| **인증** | Bearer Token 필요 |
| **설명** | 사용자의 비밀번호를 변경합니다. |

#### **요청 파라미터**
```json
{
  "currentPassword": "OldPassword123!",
  "newPassword": "NewPassword456!"
}
```

#### **응답 예시**
```json
{
  "success": true,
  "message": "비밀번호가 성공적으로 변경되었습니다."
}
```

---

## 🤖 4. AI 분석 API

### **4.1 콘텐츠 업로드 및 분석**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 콘텐츠 업로드 및 AI 분석 |
| **Method** | POST |
| **URL** | `/ai/analyze` |
| **인증** | Bearer Token 필요 |
| **설명** | 이미지와 텍스트를 업로드하여 AI 분석을 수행합니다. |

#### **요청 파라미터 (Multipart Form Data)**
```
title: "가족 여행 사진"
description: "제주도 여행에서 찍은 가족 사진입니다."
file: [이미지 파일]
category: "FAMILY"
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "contentId": 456,
    "analysisId": 789,
    "analysis": {
      "keywords": ["가족", "여행", "제주도", "바다", "자연"],
      "similarWords": ["휴가", "관광", "풍경", "추억"],
      "emotionScore": 0.85,
      "confidenceScore": 0.92,
      "modelVersion": "word2vec_v1.0"
    },
    "status": "ANALYZED"
  },
  "message": "AI 분석이 완료되었습니다."
}
```

### **4.2 AI 분석 결과 조회**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | AI 분석 결과 조회 |
| **Method** | GET |
| **URL** | `/ai/analyses/{analysisId}` |
| **인증** | Bearer Token 필요 |
| **설명** | 특정 AI 분석 결과를 조회합니다. |

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "id": 789,
    "contentId": 456,
    "analysisType": "IMAGE_TEXT",
    "keywords": ["가족", "여행", "제주도", "바다", "자연"],
    "similarWords": ["휴가", "관광", "풍경", "추억"],
    "emotionScore": 0.85,
    "confidenceScore": 0.92,
    "modelVersion": "word2vec_v1.0",
    "analysisData": {
      "imageObjects": ["사람", "바다", "하늘", "나무"],
      "textSentiment": "긍정적",
      "language": "ko"
    },
    "createdAt": "2025-01-15T10:30:00Z"
  }
}
```

---

## 🎮 5. 게임 시스템 API

### **5.1 게임 세션 시작**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 게임 세션 시작 |
| **Method** | POST |
| **URL** | `/games/sessions` |
| **인증** | Bearer Token 필요 |
| **설명** | 새로운 게임 세션을 시작합니다. |

#### **요청 파라미터**
```json
{
  "sessionType": "STANDARD",
  "difficultyLevel": 2,
  "totalQuestions": 10
}
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "sessionId": 101,
    "sessionType": "STANDARD",
    "difficultyLevel": 2,
    "totalQuestions": 10,
    "status": "ACTIVE",
    "startTime": "2025-01-15T10:30:00Z",
    "questions": [
      {
        "id": 201,
        "contentId": 456,
        "questionText": "이 이미지와 가장 관련이 깊은 단어는?",
        "options": ["가족", "여행", "바다", "음식"],
        "correctAnswer": "가족"
      }
    ]
  },
  "message": "게임 세션이 시작되었습니다."
}
```

### **5.2 게임 답변 제출**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 게임 답변 제출 |
| **Method** | POST |
| **URL** | `/games/sessions/{sessionId}/answers` |
| **인증** | Bearer Token 필요 |
| **설명** | 게임 문제에 대한 답변을 제출합니다. |

#### **요청 파라미터**
```json
{
  "questionId": 201,
  "userAnswer": "가족",
  "responseTimeMs": 2500,
  "confidenceLevel": 0.9
}
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "answerId": 301,
    "isCorrect": true,
    "score": 95,
    "correctAnswer": "가족",
    "explanation": "정답입니다! 이 이미지는 가족 여행을 보여주고 있습니다."
  },
  "message": "답변이 제출되었습니다."
}
```

### **5.3 게임 세션 완료**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 게임 세션 완료 |
| **Method** | PUT |
| **URL** | `/games/sessions/{sessionId}/complete` |
| **인증** | Bearer Token 필요 |
| **설명** | 게임 세션을 완료하고 최종 결과를 반환합니다. |

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "sessionId": 101,
    "totalScore": 850,
    "correctAnswers": 8,
    "totalQuestions": 10,
    "accuracy": 0.8,
    "averageResponseTime": 3200,
    "difficultyLevel": 2,
    "completionTime": "2025-01-15T10:45:00Z",
    "recommendations": [
      "정답률이 높습니다. 난이도를 높여보세요.",
      "반응시간이 빠릅니다. 더 신중하게 생각해보세요."
    ]
  },
  "message": "게임 세션이 완료되었습니다."
}
```

---

## 📊 6. 진행도 추적 API

### **6.1 게임 통계 조회**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 게임 통계 조회 |
| **Method** | GET |
| **URL** | `/dashboard/statistics` |
| **인증** | Bearer Token 필요 |
| **설명** | 사용자의 게임 통계 정보를 조회합니다. |

#### **쿼리 파라미터**
```
?period=daily&startDate=2025-01-01&endDate=2025-01-15
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "totalSessions": 25,
    "totalScore": 21500,
    "averageScore": 860,
    "accuracy": 0.78,
    "averageResponseTime": 3500,
    "dailyProgress": [
      {
        "date": "2025-01-15",
        "sessions": 2,
        "score": 1750,
        "accuracy": 0.85
      }
    ],
    "categoryPerformance": {
      "FAMILY": 0.82,
      "TRAVEL": 0.75,
      "NATURE": 0.80
    }
  }
}
```

### **6.2 진행도 차트 데이터**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 진행도 차트 데이터 |
| **Method** | GET |
| **URL** | `/dashboard/charts` |
| **인증** | Bearer Token 필요 |
| **설명** | 차트 표시에 필요한 진행도 데이터를 조회합니다. |

#### **쿼리 파라미터**
```
?chartType=weekly&metric=accuracy
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "chartType": "weekly",
    "metric": "accuracy",
    "labels": ["1주차", "2주차", "3주차", "4주차"],
    "datasets": [
      {
        "label": "정답률",
        "data": [0.75, 0.78, 0.82, 0.85],
        "borderColor": "#4CAF50",
        "backgroundColor": "rgba(76, 175, 80, 0.1)"
      }
    ]
  }
}
```

---

## 👨‍👩‍👧‍👦 7. 가족 공유 API

### **7.1 가족 그룹 생성**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 가족 그룹 생성 |
| **Method** | POST |
| **URL** | `/family/groups` |
| **인증** | Bearer Token 필요 |
| **설명** | 새로운 가족 그룹을 생성합니다. |

#### **요청 파라미터**
```json
{
  "name": "홍길동 가족",
  "description": "치매 예방을 위한 가족 그룹입니다.",
  "maxMembers": 5
}
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "groupId": 501,
    "name": "홍길동 가족",
    "description": "치매 예방을 위한 가족 그룹입니다.",
    "inviteCode": "ABC123",
    "maxMembers": 5,
    "createdBy": 123,
    "createdAt": "2025-01-15T10:30:00Z"
  },
  "message": "가족 그룹이 생성되었습니다."
}
```

### **7.2 가족 그룹 참여**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 가족 그룹 참여 |
| **Method** | POST |
| **URL** | `/family/groups/join` |
| **인증** | Bearer Token 필요 |
| **설명** | 초대 코드를 사용하여 가족 그룹에 참여합니다. |

#### **요청 파라미터**
```json
{
  "inviteCode": "ABC123",
  "relationship": "자녀"
}
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "groupId": 501,
    "groupId": 501,
    "role": "MEMBER",
    "relationship": "자녀",
    "joinedAt": "2025-01-15T10:35:00Z"
  },
  "message": "가족 그룹에 참여했습니다."
}
```

### **7.3 가족 진행도 모니터링**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 가족 진행도 모니터링 |
| **Method** | GET |
| **URL** | `/family/monitor/{userId}` |
| **인증** | Bearer Token 필요 |
| **설명** | 가족 구성원의 게임 진행도를 모니터링합니다. |

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "userId": 124,
    "name": "홍어머니",
    "relationship": "어머니",
    "recentProgress": {
      "lastSessionDate": "2025-01-15",
      "weeklySessions": 5,
      "weeklyAverageScore": 820,
      "weeklyAccuracy": 0.78
    },
    "trends": {
      "scoreTrend": "increasing",
      "accuracyTrend": "stable",
      "responseTimeTrend": "decreasing"
    },
    "recommendations": [
      "정답률이 향상되고 있습니다.",
      "더 어려운 문제에 도전해보세요."
    ]
  }
}
```

---

## 🔔 8. 알림 시스템 API

### **8.1 알림 목록 조회**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 알림 목록 조회 |
| **Method** | GET |
| **URL** | `/notifications` |
| **인증** | Bearer Token 필요 |
| **설명** | 사용자의 알림 목록을 조회합니다. |

#### **쿼리 파라미터**
```
?page=1&size=20&type=GAME_COMPLETE&unreadOnly=true
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": 601,
        "type": "GAME_COMPLETE",
        "title": "게임 완료",
        "message": "오늘의 게임을 완료했습니다. 정답률: 85%",
        "isRead": false,
        "createdAt": "2025-01-15T10:45:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "totalElements": 45,
      "totalPages": 3
    }
  }
}
```

### **8.2 알림 읽음 처리**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 알림 읽음 처리 |
| **Method** | PUT |
| **URL** | `/notifications/{notificationId}/read` |
| **인증** | Bearer Token 필요 |
| **설명** | 특정 알림을 읽음 상태로 변경합니다. |

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "notificationId": 601,
    "isRead": true,
    "readAt": "2025-01-15T11:00:00Z"
  },
  "message": "알림이 읽음 처리되었습니다."
}
```

---

## 🛠️ 9. 관리자 API

### **9.1 사용자 목록 조회**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 사용자 목록 조회 |
| **Method** | GET |
| **URL** | `/admin/users` |
| **인증** | Bearer Token 필요 (ADMIN 권한) |
| **설명** | 전체 사용자 목록을 조회합니다. |

#### **쿼리 파라미터**
```
?page=1&size=50&role=USER&status=ACTIVE&search=홍길동
```

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 123,
        "email": "user@example.com",
        "name": "홍길동",
        "role": "USER",
        "status": "ACTIVE",
        "emailVerified": true,
        "createdAt": "2025-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 50,
      "totalElements": 1250,
      "totalPages": 25
    }
  }
}
```

### **9.2 시스템 통계**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 시스템 통계 |
| **Method** | GET |
| **URL** | `/admin/statistics` |
| **인증** | Bearer Token 필요 (ADMIN 권한) |
| **설명** | 전체 시스템의 통계 정보를 조회합니다. |

#### **응답 예시**
```json
{
  "success": true,
  "data": {
    "userStatistics": {
      "totalUsers": 1250,
      "activeUsers": 980,
      "newUsersThisMonth": 45,
      "verifiedUsers": 1200
    },
    "gameStatistics": {
      "totalSessions": 12500,
      "totalScore": 1050000,
      "averageScore": 840,
      "averageAccuracy": 0.76
    },
    "aiStatistics": {
      "totalAnalyses": 8900,
      "averageConfidence": 0.88,
      "modelVersion": "word2vec_v1.0"
    },
    "systemHealth": {
      "databaseStatus": "HEALTHY",
      "aiServiceStatus": "HEALTHY",
      "uptime": "99.9%",
      "lastBackup": "2025-01-15T02:00:00Z"
    }
  }
}
```

---

## 📝 10. 에러 코드 정의

### **10.1 공통 에러 코드**

| 에러 코드 | HTTP 상태 | 설명 |
| --- | --- | --- |
| `INVALID_REQUEST` | 400 | 잘못된 요청 형식 |
| `UNAUTHORIZED` | 401 | 인증이 필요합니다 |
| `FORBIDDEN` | 403 | 권한이 없습니다 |
| `RESOURCE_NOT_FOUND` | 404 | 리소스를 찾을 수 없습니다 |
| `VALIDATION_ERROR` | 400 | 데이터 검증 실패 |
| `INTERNAL_SERVER_ERROR` | 500 | 서버 내부 오류 |

### **10.2 비즈니스 에러 코드**

| 에러 코드 | HTTP 상태 | 설명 |
| --- | --- | --- |
| `USER_NOT_FOUND` | 404 | 사용자를 찾을 수 없습니다 |
| `EMAIL_ALREADY_EXISTS` | 409 | 이미 존재하는 이메일입니다 |
| `INVALID_CREDENTIALS` | 401 | 잘못된 인증 정보입니다 |
| `EMAIL_NOT_VERIFIED` | 403 | 이메일 인증이 필요합니다 |
| `GAME_SESSION_NOT_FOUND` | 404 | 게임 세션을 찾을 수 없습니다 |
| `INSUFFICIENT_PERMISSIONS` | 403 | 권한이 부족합니다 |

---

## 🔧 11. API 테스트

### **11.1 Swagger UI**
- **URL**: `http://localhost:8080/swagger-ui.html`
- **설명**: API 문서화 및 테스트 도구

### **11.2 Postman Collection**
- **파일**: `MemoryForest_API.postman_collection.json`
- **설명**: API 테스트를 위한 Postman 컬렉션

### **11.3 테스트 환경**
- **개발**: `http://localhost:8080/api/v1`
- **스테이징**: `https://staging.memoryforest.com/api/v1`
- **운영**: `https://api.memoryforest.com/api/v1`

---

**문서 정보**
- 작성일: 2025년 1월 15일
- 버전: v1.0
- 작성자: 백엔드 개발자
- 검토자: 프론트엔드 개발자
- 승인자: 기술 책임자
