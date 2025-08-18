FROM eclipse-temurin:21-jdk-alpine as builder
WORKDIR /app

# Gradle 래퍼와 설정 파일 복사
COPY backend/SpringBoot/gradle/wrapper /app/gradle/wrapper
COPY backend/SpringBoot/settings.gradle /app/settings.gradle
COPY backend/SpringBoot/build.gradle /app/build.gradle
COPY backend/SpringBoot/gradlew /app/gradlew

# 권한 설정
RUN chmod +x ./gradlew

# 의존성 다운로드 (캐시 활용)
RUN ./gradlew dependencies

# 소스 코드 복사
COPY backend/SpringBoot/src /app/src

# 빌드 실행
RUN ./gradlew build -x test

FROM eclipse-temurin:21-jdk-alpine
WORKDIR /app

RUN apk add --no-cache tzdata
ENV TZ=Asia/Seoul

COPY --from=builder /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]