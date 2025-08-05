# Build stage
FROM node:20 AS build

# 보안을 위한 non-root 사용자 설정
RUN groupadd -g 1001 nodejs \
  && useradd -m -u 1001 -g nodejs nextjs

WORKDIR /app

# 패키지 파일들 복사 (프로젝트 루트에서 frontend 폴더로)
COPY frontend/package*.json ./

# 의존성 설치
RUN npm install

# 소스 코드 복사
COPY frontend/ .

# 소유권 변경
RUN chown -R nextjs:nodejs /app
USER nextjs

# 빌드 실행
RUN npm run build

# Production stage
FROM nginx:1.28.0

# 보안을 위한 패키지 업데이트
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 기본 nginx 설정 제거
RUN rm /etc/nginx/conf.d/default.conf

# 커스텀 nginx 설정 추가
COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf

# 빌드된 파일들 복사
COPY --from=build /app/dist /usr/share/nginx/html

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# 포트 노출
EXPOSE 80

# nginx 실행
CMD ["nginx", "-g", "daemon off;"]