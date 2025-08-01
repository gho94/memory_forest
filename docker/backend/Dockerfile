FROM eclipse-temurin:21-jdk-alpine as builder
WORKDIR /app

COPY gradle/wrapper /app/gradle/wrapper
COPY settings.gradle /app/settings.gradle
COPY build.gradle /app/build.gradle
COPY gradlew /app/gradlew

# 의존성 설치 (캐시 활용)
RUN ./gradlew build -x test

# 소스 코드 복사 (변경이 자주 되는 파일들)
COPY src /app/src

RUN ./gradlew build -x test

FROM eclipse-temurin:21-jdk-alpine
WORKDIR /app
COPY --from=builder /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]