# 📄 **API 명세서 (API Specification)**

> **프로젝트명**: Memory Forest - AI 기반 치매 케어 인지 훈련 플랫폼
> 
> **작성일**: 2025.01.15
> 
> **작성자**: 백엔드 개발자

---

## 📋 1. API 개요

### **1.1 기본 정보**
- **Base URL**: `http://localhost:8080`
- **인증 방식**: Session 기반 인증
- **응답 형식**: JSON
- **문자 인코딩**: UTF-8

### **1.2 공통 응답 형식**

#### **성공 응답**
```json
{
  "success": true,
  "data": {},
  "message": "요청이 성공적으로 처리되었습니다."
}
```

#### **에러 응답**
```json
{
  "success": false,
  "message": "오류가 발생했습니다."
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

### **2.1 로그인**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 로그인 |
| **Method** | POST |
| **URL** | `/api/auth/login` |
| **설명** | 로그인 ID와 비밀번호로 로그인하여 세션을 생성합니다. |

#### **요청 파라미터**
```json
{
  "loginId": "user123",
  "password": "SecurePassword123!"
}
```

#### **응답 예시**
```json
{
  "success": true,
  "message": "로그인 성공",
  "userId": "user123",
  "loginId": "user123",
  "userName": "홍길동",
  "userTypeCode": "COMPANION",
  "email": "user@example.com"
}
```

### **2.2 API 테스트**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | API 테스트 |
| **Method** | GET |
| **URL** | `/api/auth/test` |
| **설명** | API 작동 상태를 확인합니다. |

#### **응답 예시**
```json
"API 작동 중!"
```

---

## 👤 3. 사용자 관리 API

### **3.1 동반자 사용자 마이페이지 조회**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 동반자 마이페이지 조회 |
| **Method** | GET |
| **URL** | `/companion/mypage` |
| **인증** | Session 필요 |
| **설명** | 동반자 사용자의 마이페이지 정보를 조회합니다. |

#### **쿼리 파라미터**
```
?userId=user123
```

#### **응답 예시**
```json
{
  "userId": "user123",
  "loginId": "user123",
  "userName": "홍길동",
  "userTypeCode": "COMPANION",
  "email": "user@example.com"
}
```

### **3.2 기록자 사용자 생성**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 기록자 사용자 생성 |
| **Method** | POST |
| **URL** | `/api/recorder/create` |
| **인증** | Session 필요 |
| **설명** | 새로운 기록자 사용자를 생성합니다. |

#### **요청 파라미터**
```json
{
  "loginId": "recorder123",
  "password": "SecurePassword123!",
  "userName": "김기록",
  "email": "recorder@example.com"
}
```

#### **응답 예시**
```json
{
  "userId": "recorder123",
  "loginId": "recorder123",
  "userName": "김기록",
  "userTypeCode": "RECORDER",
  "email": "recorder@example.com"
}
```

### **3.3 기록자 사용자 수정**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 기록자 사용자 수정 |
| **Method** | POST |
| **URL** | `/api/recorder/update` |
| **인증** | Session 필요 |
| **설명** | 기록자 사용자 정보를 수정합니다. |

#### **요청 파라미터**
```json
{
  "userId": "recorder123",
  "userName": "김기록수정",
  "email": "updated@example.com"
}
```

### **3.4 기록자 목록 조회**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 기록자 목록 조회 |
| **Method** | GET |
| **URL** | `/api/recorder/list` |
| **인증** | Session 필요 |
| **설명** | 특정 사용자와 연결된 기록자 목록을 조회합니다. |

#### **쿼리 파라미터**
```
?userId=user123
```

---

## 🎮 4. 게임 시스템 API

### **4.1 게임 생성**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 게임 생성 |
| **Method** | POST |
| **URL** | `/api/game` |
| **인증** | Session 필요 |
| **설명** | 새로운 게임을 생성합니다. |

#### **요청 파라미터**
```json
{
  "gameName": "기억력 게임",
  "gameType": "MEMORY",
  "difficulty": "MEDIUM"
}
```

### **4.2 게임 수정**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 게임 수정 |
| **Method** | POST |
| **URL** | `/api/game/update` |
| **인증** | Session 필요 |
| **설명** | 기존 게임 정보를 수정합니다. |

### **4.3 동반자 게임 대시보드**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 동반자 게임 대시보드 |
| **Method** | GET |
| **URL** | `/companion/dashboard` |
| **인증** | Session 필요 |
| **설명** | 동반자용 게임 대시보드 정보를 조회합니다. |

### **4.4 동반자 게임 목록**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 동반자 게임 목록 |
| **Method** | GET |
| **URL** | `/companion/games/list` |
| **인증** | Session 필요 |
| **설명** | 특정 게임의 상세 정보를 조회합니다. |

#### **쿼리 파라미터**
```
?gameId=game123
```

### **4.5 동반자 게임 세션 생성**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 동반자 게임 세션 생성 |
| **Method** | POST |
| **URL** | `/companion/game/sessions` |
| **인증** | Session 필요 |
| **설명** | 동반자용 게임 세션을 생성합니다. |

### **4.6 동반자 게임 상태 변경**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 동반자 게임 상태 변경 |
| **Method** | PUT |
| **URL** | `/companion/game/sessions/{sessionId}/status` |
| **인증** | Session 필요 |
| **설명** | 동반자 게임 세션의 상태를 변경합니다. |

### **4.7 동반자 게임 일괄 완료 처리**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 동반자 게임 일괄 완료 |
| **Method** | POST |
| **URL** | `/companion/game/batch/completed` |
| **인증** | Session 필요 |
| **설명** | 여러 게임을 일괄적으로 완료 상태로 변경합니다. |

#### **요청 파라미터**
```json
["game1", "game2", "game3"]
```

### **4.8 동반자 게임 일괄 오류 처리**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 동반자 게임 일괄 오류 |
| **Method** | POST |
| **URL** | `/companion/game/batch/error` |
| **인증** | Session 필요 |
| **설명** | 여러 게임을 일괄적으로 오류 상태로 변경합니다. |

#### **요청 파라미터**
```json
{
  "gameIds": ["game1", "game2", "game3"],
  "errorDescription": "AI 분석 실패"
}
```

### **4.9 동반자 게임 대시보드 통계**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 동반자 게임 대시보드 통계 |
| **Method** | GET |
| **URL** | `/companion/game/dashboard` |
| **인증** | Session 필요 |
| **설명** | 동반자 게임 대시보드 통계 정보를 조회합니다. |

### **4.10 기록자 게임 세션 생성**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 기록자 게임 세션 생성 |
| **Method** | POST |
| **URL** | `/recorder/game/sessions` |
| **인증** | Session 필요 |
| **설명** | 기록자용 게임 세션을 생성합니다. |

### **4.11 기록자 게임 답변 제출**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 기록자 게임 답변 제출 |
| **Method** | POST |
| **URL** | `/recorder/game/sessions/{sessionId}/answers` |
| **인증** | Session 필요 |
| **설명** | 기록자 게임 문제에 대한 답변을 제출합니다. |

### **4.12 기록자 게임 세션 완료**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 기록자 게임 세션 완료 |
| **Method** | PUT |
| **URL** | `/recorder/game/sessions/{sessionId}/complete` |
| **인증** | Session 필요 |
| **설명** | 기록자 게임 세션을 완료합니다. |

### **4.13 기록자 게임 대시보드 통계**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 기록자 게임 대시보드 통계 |
| **Method** | GET |
| **URL** | `/recorder/game/dashboard` |
| **인증** | Session 필요 |
| **설명** | 기록자 게임 대시보드 통계 정보를 조회합니다. |

### **4.14 게임 상태 일괄 업데이트**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 게임 상태 일괄 업데이트 |
| **Method** | POST |
| **URL** | `/api/games/status/batch-update` |
| **인증** | Session 필요 |
| **설명** | Airflow에서 호출하여 게임 상태를 일괄 업데이트합니다. |

---

## 📝 5. 기록 관리 API

### **5.1 음성 레코드 생성**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 음성 레코드 생성 |
| **Method** | POST |
| **URL** | `/recorder/record/create` |
| **인증** | Session 필요 |
| **설명** | 음성 파일과 텍스트를 포함한 레코드를 생성합니다. |

#### **요청 파라미터**
```json
{
  "fileId": 123,
  "text": "오늘은 날씨가 좋습니다.",
  "duration": 5000
}
```

#### **응답 예시**
```json
"success"
```

### **5.2 기록자 레코드 목록 조회**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 기록자 레코드 목록 조회 |
| **Method** | GET |
| **URL** | `/recorder/record/list` |
| **인증** | Session 필요 |
| **설명** | 기록자의 레코드 목록을 조회합니다. |

### **5.3 동반자 레코드 대시보드 통계**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 동반자 레코드 대시보드 통계 |
| **Method** | GET |
| **URL** | `/companion/record/dashboard` |
| **인증** | Session 필요 |
| **설명** | 동반자 레코드 대시보드 통계 정보를 조회합니다. |

---

## 🤖 6. AI 분석 API

### **6.1 AI 분석 테스트**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | AI 분석 테스트 |
| **Method** | POST |
| **URL** | `/api/test/ai-analysis` |
| **인증** | Session 필요 |
| **설명** | AI 분석 기능을 테스트합니다. |

#### **요청 파라미터**
```json
{
  "text": "테스트 텍스트",
  "imageUrl": "https://example.com/image.jpg"
}
```

---

## 🛠️ 7. 공통 기능 API

### **7.1 공통 코드 조회**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 공통 코드 조회 |
| **Method** | GET |
| **URL** | `/api/common-codes` |
| **설명** | 공통 코드 목록을 조회합니다. |

#### **쿼리 파라미터**
```
?parentCodeID=USER_TYPE
```

### **7.2 공통 코드 개별 조회**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 공통 코드 개별 조회 |
| **Method** | GET |
| **URL** | `/api/common-codes/{codeId}` |
| **설명** | 특정 공통 코드 정보를 조회합니다. |

### **7.3 공통 코드 생성**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 공통 코드 생성 |
| **Method** | POST |
| **URL** | `/api/common-codes` |
| **설명** | 새로운 공통 코드를 생성합니다. |

### **7.4 공통 코드 수정**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 공통 코드 수정 |
| **Method** | PUT |
| **URL** | `/api/common-codes/{codeId}` |
| **설명** | 기존 공통 코드를 수정합니다. |

### **7.5 공통 코드 삭제**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 공통 코드 삭제 |
| **Method** | DELETE |
| **URL** | `/api/common-codes/{codeId}` |
| **설명** | 공통 코드를 삭제합니다. |

### **7.6 파일 업로드**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 파일 업로드 |
| **Method** | POST |
| **URL** | `/api/files/upload` |
| **설명** | S3에 파일을 업로드합니다. |

#### **요청 파라미터**
```
file: [파일]
```

### **7.7 파일 정보 조회**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 파일 정보 조회 |
| **Method** | GET |
| **URL** | `/api/files/{fileId}` |
| **설명** | 파일 ID로 파일 정보를 조회합니다. |

---

## 🔔 8. 알림 시스템 API

### **8.1 알림 목록 조회**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 알림 목록 조회 |
| **Method** | GET |
| **URL** | `/api/alarms` |
| **인증** | Session 필요 |
| **설명** | 사용자의 알림 목록을 조회합니다. |

#### **응답 예시**
```json
[
  {
    "alarmId": 1,
    "title": "게임 완료",
    "message": "오늘의 게임을 완료했습니다.",
    "isRead": false,
    "createdAt": "2025-01-15T10:30:00Z"
  }
]
```

### **8.2 알림 읽음 처리**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 알림 읽음 처리 |
| **Method** | PUT |
| **URL** | `/api/alarms/{alarmId}/read` |
| **인증** | Session 필요 |
| **설명** | 특정 알림을 읽음 상태로 변경합니다. |

---

## 📊 9. 대시보드 API

### **9.1 동반자 게임 대시보드**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 동반자 게임 대시보드 |
| **Method** | GET |
| **URL** | `/companion/game/dashboard` |
| **인증** | Session 필요 |
| **설명** | 동반자용 게임 대시보드 통계를 조회합니다. |

### **9.2 동반자 레코드 대시보드**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 동반자 레코드 대시보드 |
| **Method** | GET |
| **URL** | `/companion/record/dashboard` |
| **인증** | Session 필요 |
| **설명** | 동반자용 레코드 대시보드 통계를 조회합니다. |

### **9.3 기록자 게임 대시보드**

| 항목 | 내용 |
| --- | --- |
| **API 이름** | 기록자 게임 대시보드 |
| **Method** | GET |
| **URL** | `/recorder/game/dashboard` |
| **인증** | Session 필요 |
| **설명** | 기록자용 게임 대시보드 통계를 조회합니다. |

---

## 🔧 10. API 테스트

### **10.1 테스트 컨트롤러**
- **URL**: `/api/test/ai-analysis`
- **설명**: AI 분석 기능 테스트

### **10.2 테스트 환경**
- **개발**: `http://localhost:8080`
- **설명**: 로컬 개발 환경

---

## 📝 11. 주요 변경사항

### **11.1 인증 방식**
- **기존**: JWT Bearer Token
- **변경**: Session 기반 인증

### **11.2 API 경로**
- **기존**: `/api/v1/...`
- **변경**: `/api/...`, `/companion/...`, `/recorder/...`

### **11.3 사용자 역할**
- **동반자 (Companion)**: 치매 환자를 돌보는 사람
- **기록자 (Recorder)**: 실제 게임을 수행하는 사람

### **11.4 게임 시스템**
- **동반자 게임**: 동반자가 관리하는 게임
- **기록자 게임**: 기록자가 실제로 수행하는 게임

---

**문서 정보**
- 작성일: 2025년 1월 15일
- 버전: v2.0
- 작성자: 백엔드 개발자
- 검토자: 프론트엔드 개발자
- 승인자: 기술 책임자
- **주요 변경**: 실제 구현된 소스 코드 기반으로 API 명세서 수정
