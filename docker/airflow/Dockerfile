FROM apache/airflow:2.7.1-python3.9

USER root

# 시스템 패키지 및 Java 설치 (AI 처리용)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    python3-dev \
    g++ \
    openjdk-17-jdk \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# JAVA 환경변수 설정
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

USER airflow

# Airflow용 requirements 설치
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    numpy==1.24.4 \
    scipy==1.10.1 \
    gensim==4.3.2 \
    && pip install --no-cache-dir -r /requirements.txt

# 모델 디렉토리 생성
RUN mkdir -p /opt/airflow/models

EXPOSE 8080