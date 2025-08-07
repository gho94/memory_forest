FROM python:3.9-slim

WORKDIR /app

# 시스템 패키지 및 Java 설치
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    python3-dev \
    g++ \
    openjdk-17-jdk \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# JAVA 환경변수 설정 (konlpy 용)
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# AI 서비스용 requirements 파일 복사 및 설치
COPY ai/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    numpy==1.24.4 \
    scipy==1.10.1 \
    gensim==4.3.2 \
    && pip install --no-cache-dir -r requirements.txt

# ai 폴더 전체 복사
COPY ai/ ./

# 모델 디렉토리 생성
RUN mkdir -p /app/models

# PYTHONPATH 설정
ENV PYTHONPATH=/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]