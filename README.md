# 🌳 **Memory Forest - AI 기반 치매 케어 인지 훈련 플랫폼**

> **AI 기술을 활용하여 치매 환자와 가족에게 실질적인 도움을 제공하는 혁신적인 서비스**

---

## 📋 **프로젝트 개요**

Memory Forest는 AI 기술을 활용하여 치매 환자와 가족에게 실질적인 도움을 제공하는 혁신적인 서비스입니다. 개인화된 인지 훈련을 통해 환자의 삶의 질을 향상시키고, 가족의 돌봄 부담을 경감하는 것을 목표로 합니다.

### **🎯 주요 목표**
- 치매 노인의 인지 기능 유지 및 개선
- 가족 중심의 돌봄 지원 시스템 구축
- AI 기반 개인화 훈련을 통한 치료 효과 극대화
- 사회적 돌봄 비용 절감 기여

### **🚀 핵심 기능**
- **AI 기반 콘텐츠 분석**: 이미지 및 텍스트 분석을 통한 개인화된 콘텐츠 생성
- **인지 훈련 게임**: 이미지-명사 매칭 게임을 통한 인지 능력 향상
- **진행도 추적**: 다차원 성과 분석 및 트렌드 모니터링
- **가족 공유 시스템**: 환자의 진행 상황을 가족과 공유하여 돌봄 지원

---

## 🏗️ **시스템 아키텍처**

### **기술 스택**
- **Backend**: Spring Boot 3.x, Java 17, MySQL 8.x
- **Frontend**: React 18, TypeScript, Vite
- **AI Service**: FastAPI, Python 3.10, Word2Vec, KoNLPy
- **Infrastructure**: Docker, Docker Compose, Nginx
- **CI/CD**: GitHub Actions

### **아키텍처 구조**
```
[React Frontend] ↔ [Spring Boot API Gateway] ↔ [Microservices]
                                                      ↓
                   [MySQL Database] ↔ [Redis Cache] ↔ [AI Engine]
                                                      ↓
                              [File Storage (AWS S3/Local)]
```

---

## 📚 **프로젝트 문서**

### **📋 기획 및 설계 문서**
- [📄 프로젝트 개요서](docs/01_프로젝트_개요서.md) - 프로젝트 기본 정보 및 개요
- [📋 요구사항 정의서](docs/02_요구사항_정의서.md) - 기능 및 비기능 요구사항 정의
- [🗂️ ERD 설계서](docs/03_ERD_설계서.md) - 데이터베이스 설계 및 관계 정의
- [🔌 API 명세서](docs/04_API_명세서.md) - REST API 엔드포인트 명세
- [🎨 화면 설계서](docs/05_화면_설계서.md) - UI/UX 설계 및 화면 구성

### **🏗️ 기술 및 개발 문서**
- [🏛️ 시스템 아키텍처](docs/06_시스템_아키텍처.md) - 전체 시스템 구조 및 설계
- [📦 배포 가이드](docs/07_배포_가이드.md) - 배포 환경 구축 및 운영 가이드
- [📅 일정표 및 마일스톤](docs/08_일정표_및_마일스톤.md) - 프로젝트 일정 및 주요 마일스톤
- [📊 WBS](docs/09_WBS.md) - 작업 분해 구조 및 상세 계획
- [📝 회의록 템플릿](docs/10_회의록_템플릿.md) - 회의록 작성 표준 템플릿

### **📖 상세 명세서**
- [👥 유스케이스 명세서](docs/11_유스케이스_명세서.md) - 사용자 시나리오 및 기능 명세
- [⚙️ 기능 명세서](docs/12_기능_명세서.md) - 상세 기능 정의 및 구현 가이드
- [📊 UML 다이어그램](docs/13_UML_다이어그램.md) - 클래스, 시퀀스, 상태 다이어그램
- [📝 코딩 컨벤션](docs/14_코딩_컨벤션.md) - 개발 언어별 코딩 표준 및 가이드라인

---

## 🚀 **빠른 시작**

### **사전 요구사항**
- Java 17+
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- MySQL 8.x

### **개발 환경 구축**
```bash
# 1. 저장소 클론
git clone https://github.com/your-username/memory-forest.git
cd memory-forest

# 2. Docker 환경 실행
docker-compose up -d

# 3. 백엔드 실행
cd backend/SpringBoot
./gradlew bootRun

# 4. 프론트엔드 실행
cd frontend
npm install
npm run dev

# 5. AI 서비스 실행
cd ai
pip install -r requirements.txt
python main.py
```

### **환경 변수 설정**
```bash
# .env 파일 생성
cp .env.example .env

# 필요한 환경 변수 설정
DB_HOST=localhost
DB_PORT=3306
DB_NAME=memory_forest
DB_USER=root
DB_PASSWORD=password

AI_SERVICE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

---

## 🎮 **주요 기능**

### **1. AI 기반 콘텐츠 분석**
- **이미지 분석**: 객체 인식 및 태그 생성
- **텍스트 분석**: 키워드 추출 및 감정 분석
- **Word2Vec 모델**: 의미적 유사도 계산 및 연관어 생성

### **2. 인지 훈련 게임**
- **이미지-명사 매칭**: 4지선다 게임을 통한 인지 훈련
- **적응형 난이도**: 사용자 성과에 따른 동적 난이도 조절
- **즉시 피드백**: 정답 여부 및 점수 즉시 제공

### **3. 진행도 추적 시스템**
- **다차원 분석**: 정확도, 반응시간, 일관성 지표 추적
- **트렌드 분석**: 장기 변화 추이 및 개선 방향 제시
- **리포트 생성**: 일간/주간/월간 성과 리포트

### **4. 가족 공유 시스템**
- **진행도 공유**: 환자의 게임 성과를 가족과 실시간 공유
- **알림 시스템**: 게임 리마인더 및 성과 업데이트 알림
- **가족 그룹 관리**: 다중 환자 지원 및 권한 관리

---

## 🔒 **보안 및 개인정보 보호**

### **보안 조치**
- **암호화**: AES-256 (저장), TLS 1.3 (전송)
- **인증**: JWT + OAuth2 (Naver 연동)
- **권한 관리**: RBAC 기반 세분화된 접근 제어
- **감사 로그**: 모든 민감한 작업 로깅

### **개인정보 보호**
- **데이터 최소화**: 필요한 정보만 수집
- **목적 제한**: 명시된 목적에만 사용
- **보존 기간**: 법적 요구사항 준수
- **삭제 권리**: 사용자 요청 시 완전 삭제

---

## 📊 **성과 지표 (KPI)**

### **사용자 참여 지표**
- **일일 활성 사용자 (DAU)**: 목표 70%
- **게임 완료율**: 목표 85%
- **평균 세션 시간**: 목표 15분
- **주간 재방문율**: 목표 80%

### **인지 성과 지표**
- **정답률 개선**: 월 평균 5% 향상
- **반응시간 단축**: 월 평균 10% 개선
- **일관성 지수**: 변동 계수 20% 이하

---

## 🧪 **테스트**

### **테스트 실행**
```bash
# 백엔드 테스트
cd backend/SpringBoot
./gradlew test

# 프론트엔드 테스트
cd frontend
npm test

# AI 서비스 테스트
cd ai
python -m pytest
```

### **테스트 커버리지**
- **백엔드**: 80% 이상
- **프론트엔드**: 70% 이상
- **AI 서비스**: 75% 이상

---

## 🚀 **배포**

### **개발 환경**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### **운영 환경**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### **배포 환경**
- **개발**: AWS EC2 (t3.medium)
- **스테이징**: AWS EC2 (t3.large)
- **운영**: AWS ECS + RDS + S3

---

## 🤝 **기여하기**

### **개발 가이드**
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### **코딩 컨벤션**
- [📝 코딩 컨벤션 가이드](docs/14_코딩_컨벤션.md) 참조
- ESLint, Prettier, Checkstyle 규칙 준수
- 테스트 코드 작성 필수

---

## 📞 **연락처 및 지원**

### **팀 구성**
- **프로젝트 매니저**: 전체 프로젝트 관리
- **백엔드 개발자** (2명): Spring Boot, AI 모델 통합
- **프론트엔드 개발자** (2명): React, UI/UX 구현
- **AI 엔지니어** (1명): 모델 개발 및 최적화
- **QA 엔지니어** (1명): 품질 관리
- **DevOps 엔지니어** (1명): 인프라 관리

### **연락처**
- **이메일**: contact@memoryforest.com
- **GitHub**: [https://github.com/your-username/memory-forest](https://github.com/your-username/memory-forest)
- **문서**: [https://docs.memoryforest.com](https://docs.memoryforest.com)

---

## 📄 **라이선스**

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🙏 **감사의 말**

- **의료진**: 신경과 전문의, 작업치료사
- **UX 전문가**: 고령자 인터페이스 전문가
- **보안 전문가**: 개인정보보호 컨설턴트
- **오픈소스 커뮤니티**: 다양한 라이브러리 및 도구 제공

---

**© 2025 Memory Forest. All rights reserved.**

> **"AI 기술로 치매 환자와 가족의 삶을 더 나은 방향으로 변화시키겠습니다."**