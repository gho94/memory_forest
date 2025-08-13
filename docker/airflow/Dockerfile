FROM apache/airflow:2.7.1-python3.9

USER root

# 시스템 패키지 및 Java 설치 (Bullseye에서는 17이 최신)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    python3-dev \
    g++ \
    htop \
    openjdk-17-jdk \
    ca-certificates \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# JAVA 환경변수 설정 (17로 맞춤)
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

USER airflow

# Airflow용 requirements 설치
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    scipy==1.10.1 \
    gensim==4.3.2 \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# KoNLPy 초기화 테스트
RUN python -c "import konlpy; from konlpy.tag import Okt; okt = Okt()" || true

# 권한 설정
USER root
RUN mkdir -p /opt/airflow/dags/utils && \
    chown -R airflow:root /opt/airflow/dags

USER airflow

# 모델 디렉토리 생성
RUN mkdir -p /opt/airflow/models

EXPOSE 8080