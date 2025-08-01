# Build stage
FROM node:20 AS build

# 보안을 위한 non-root 사용자 설정
RUN groupadd -g 1001 nodejs \
  && useradd -m -u 1001 -g nodejs nextjs

WORKDIR /app

# 현재 위치와 상위 디렉토리 확인
RUN pwd && ls -la .

# 패키지 파일들 복사 (context가 프로젝트 루트라면)
COPY ./frontend/package*.json ./

# 디버깅: 파일이 제대로 복사되었는지 확인
#RUN ls -la /app/ && echo "=== package.json content ===" && head -10 /app/package.json

# 의존성 설치
RUN npm install

# 소스 코드 복사 (docker/frontend에서 ../../frontend로 이동)
COPY ../../frontend/ .

# 소유권 변경
RUN chown -R nextjs:nodejs /app
USER nextjs

# 빌드 실행
RUN npm run build

# Production stage
FROM nginx:1.28.0

# 보안을 위한 패키지 업데이트
RUN apt-get update && apt-get install -y curl

# 기본 nginx 설정 제거
RUN rm /etc/nginx/conf.d/default.conf

# 커스텀 nginx 설정 추가 (docker/frontend에서 ../nginx로 이동)
COPY ./docker/nginx/default.conf /etc/nginx/conf.d/default.conf

# 빌드된 파일들 복사
COPY --from=build /app/dist /usr/share/nginx/html

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# 포트 노출
EXPOSE 80

# nginx 실행
CMD ["nginx", "-g", "daemon off;"]