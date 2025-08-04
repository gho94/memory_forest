-- =====================================================
-- MemoryForest Database Schema for MySQL 8.0
-- AI 기반 치매 노인 인지훈련 서비스
-- =====================================================

-- MySQL 설정
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 데이터베이스 생성 (필요시)
-- CREATE DATABASE memory_forest CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE memory_forest;

-- 공통코드 테이블
CREATE TABLE COMMON_CODES (
                              CODE_ID         CHAR(6)        NOT NULL COMMENT '공통코드 ID (6자리 고정)',
                              CODE_NAME       VARCHAR(100)   NOT NULL COMMENT '공통코드명',
                              P_CODE_ID       CHAR(6)        NULL     COMMENT '부모 코드 ID (계층 구조)',
                              USE_YN          ENUM('Y', 'N') NOT NULL DEFAULT 'Y' COMMENT '사용 여부',
                              CREATED_BY      VARCHAR(10)    NOT NULL COMMENT '생성자',
                              CREATED_AT      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
                              UPDATED_BY      VARCHAR(10)    NULL     COMMENT '수정자',
                              UPDATED_AT      TIMESTAMP      NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
                              PRIMARY KEY (CODE_ID),
                              KEY IDX_COMMON_CODES_P_CODE_ID (P_CODE_ID),
                              CONSTRAINT FK_COMMON_CODES_PARENT FOREIGN KEY (P_CODE_ID) REFERENCES COMMON_CODES(CODE_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='공통코드 관리 테이블 (계층적 구조)';

-- 파일 정보 테이블
CREATE TABLE FILE_INFO (
                           FILE_ID         INT            NOT NULL AUTO_INCREMENT COMMENT '파일 ID (자동증가)',
                           ORIGINAL_NAME   VARCHAR(255)   NOT NULL COMMENT '원본 파일명',
                           S3_KEY          VARCHAR(500)   NOT NULL COMMENT 'S3 객체 키',
                           S3_URL          VARCHAR(1000)  NOT NULL COMMENT 'S3 접근 URL',
                           BUCKET_NAME     VARCHAR(100)   NOT NULL COMMENT 'S3 버킷명',
                           FILE_SIZE       BIGINT         NULL     COMMENT '파일 크기',
                           CONTENT_TYPE    VARCHAR(100)   NULL     COMMENT '컨텐츠 타입',
                           UPLOAD_DATE     DATE           NOT NULL DEFAULT (CURDATE()) COMMENT '업로드 날짜',
                           CREATED_BY      VARCHAR(50)    NULL     COMMENT '생성자 ID',
                           IS_PUBLIC       ENUM('Y', 'N') NOT NULL DEFAULT 'N' COMMENT '공개/비공개 여부',
                           PRIMARY KEY (FILE_ID),
                           UNIQUE KEY UK_S3_KEY (S3_KEY)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AWS S3 파일 정보 테이블';

-- 사용자 테이블
CREATE TABLE USERS (
                       USER_ID           VARCHAR(10)    NOT NULL COMMENT '사용자 ID (10자리)',
                       USER_NAME         VARCHAR(100)   NOT NULL COMMENT '사용자명',
                       PASSWORD          VARCHAR(60)    NOT NULL COMMENT '암호화된 비밀번호',
                       EMAIL             VARCHAR(100)   NOT NULL COMMENT '이메일 (고유값)',
                       PHONE             VARCHAR(20)    NULL     COMMENT '전화번호',
                       USER_TYPE_CODE    CHAR(6)        NOT NULL COMMENT '사용자 유형 코드 (환자/가족/관리자/의료진)',
                       PROFILE_IMAGE_FILE_ID INT         NULL     COMMENT '프로필 이미지 파일 ID (FILE_INFO FK)',
                       STATUS_CODE       CHAR(6)        NOT NULL COMMENT '계정 상태 코드 (활성/비활성/정지/삭제)',
                       CREATED_BY        VARCHAR(10)    NOT NULL COMMENT '생성자',
                       CREATED_AT        TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
                       UPDATED_BY        VARCHAR(10)    NULL     COMMENT '수정자',
                       UPDATED_AT        TIMESTAMP      NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
                       LOGIN_AT          TIMESTAMP      NULL     COMMENT '마지막 로그인 일시',
                       PRIMARY KEY (USER_ID),
                       UNIQUE KEY UK_USERS_EMAIL (EMAIL),
                       KEY IDX_USERS_USER_TYPE (USER_TYPE_CODE),
                       KEY IDX_USERS_STATUS (STATUS_CODE),
                       CONSTRAINT FK_USERS_USER_TYPE FOREIGN KEY (USER_TYPE_CODE) REFERENCES COMMON_CODES(CODE_ID),
                       CONSTRAINT FK_USERS_STATUS FOREIGN KEY (STATUS_CODE) REFERENCES COMMON_CODES(CODE_ID),
                       CONSTRAINT FK_USERS_PROFILE_IMAGE FOREIGN KEY (PROFILE_IMAGE_FILE_ID) REFERENCES FILE_INFO(FILE_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 정보 관리 테이블';

-- 사용자 히스토리 테이블
CREATE TABLE USERS_HIST (
                            HIST_ID           INT            NOT NULL AUTO_INCREMENT COMMENT '히스토리 ID (자동 증가)',
                            ACTION_TYPE_CODE  CHAR(6)        NOT NULL COMMENT '액션 타입 코드 (생성/수정/삭제)',
                            USER_ID           VARCHAR(10)    NOT NULL COMMENT '사용자 ID',
                            USER_NAME         VARCHAR(100)   NOT NULL COMMENT '사용자명 (변경 시점)',
                            PASSWORD          VARCHAR(60)    NOT NULL COMMENT '암호화된 비밀번호 (변경 시점)',
                            EMAIL             VARCHAR(100)   NOT NULL COMMENT '이메일 (변경 시점)',
                            PHONE             VARCHAR(20)    NULL     COMMENT '전화번호 (변경 시점)',
                            USER_TYPE_CODE    CHAR(6)        NOT NULL COMMENT '사용자 유형 코드 (변경 시점)',
                            PROFILE_IMAGE     LONGTEXT       NULL     COMMENT '프로필 이미지 (변경 시점)',
                            STATUS_CODE       CHAR(6)        NOT NULL COMMENT '계정 상태 코드 (변경 시점)',
                            CREATED_AT        TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '히스토리 생성일시',
                            CHANGED_BY        VARCHAR(10)    NOT NULL COMMENT '변경자 ID',
                            PRIMARY KEY (HIST_ID),
                            KEY IDX_USERS_HIST_USER_ID (USER_ID),
                            KEY IDX_USERS_HIST_ACTION_TYPE (ACTION_TYPE_CODE),
                            KEY IDX_USERS_HIST_CREATED_AT (CREATED_AT),
                            CONSTRAINT FK_USERS_HIST_ACTION_TYPE FOREIGN KEY (ACTION_TYPE_CODE) REFERENCES COMMON_CODES(CODE_ID),
                            CONSTRAINT FK_USERS_HIST_USER_TYPE FOREIGN KEY (USER_TYPE_CODE) REFERENCES COMMON_CODES(CODE_ID),
                            CONSTRAINT FK_USERS_HIST_STATUS FOREIGN KEY (STATUS_CODE) REFERENCES COMMON_CODES(CODE_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 정보 변경 히스토리 테이블';

-- 사용자 관계 테이블
CREATE TABLE USER_REL (
                          PATIENT_ID        VARCHAR(10)    NOT NULL COMMENT '환자 ID',
                          FAMILY_ID         VARCHAR(10)    NOT NULL COMMENT '가족 ID',
                          RELATIONSHIP_CODE CHAR(6)        NOT NULL COMMENT '관계 코드 (배우자/아들/딸/손자/손녀/형제/자매)',
                          STATUS_CODE       CHAR(6)        NOT NULL COMMENT '연결 상태 코드 (연결됨/연결대기/연결해제/거부됨)',
                          CREATED_AT        TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '관계 생성일시',
                          PRIMARY KEY (PATIENT_ID, FAMILY_ID),
                          KEY IDX_USER_REL_PATIENT (PATIENT_ID),
                          KEY IDX_USER_REL_FAMILY (FAMILY_ID),
                          KEY IDX_USER_REL_STATUS (STATUS_CODE),
                          CONSTRAINT FK_USER_REL_PATIENT FOREIGN KEY (PATIENT_ID) REFERENCES USERS(USER_ID),
                          CONSTRAINT FK_USER_REL_FAMILY FOREIGN KEY (FAMILY_ID) REFERENCES USERS(USER_ID),
                          CONSTRAINT FK_USER_REL_RELATIONSHIP FOREIGN KEY (RELATIONSHIP_CODE) REFERENCES COMMON_CODES(CODE_ID),
                          CONSTRAINT FK_USER_REL_STATUS FOREIGN KEY (STATUS_CODE) REFERENCES COMMON_CODES(CODE_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 간 관계 정보 테이블 (환자-가족 연결)';

-- 게임 마스터 테이블
CREATE TABLE GAME_MASTER (
                             GAME_ID               VARCHAR(10)    NOT NULL COMMENT '게임 ID (G250717001 형식)',
                             GAME_NAME             VARCHAR(100)   NOT NULL COMMENT '게임명',
                             GAME_DESC             VARCHAR(200)   NULL     COMMENT '게임 설명',
                             GAME_COUNT            INT            NOT NULL COMMENT '게임 문제 수',
                             DIFFICULTY_LEVEL_CODE CHAR(6)        NOT NULL COMMENT '난이도 코드 (초급/중급/고급/전문가)',
                             CREATION_STATUS_CODE  CHAR(6)        NOT NULL COMMENT '생성 상태 코드 (대기중/생성중/완료/실패/취소)',
                             CREATED_BY            VARCHAR(10)    NOT NULL COMMENT '생성자 (가족 또는 관리자)',
                             CREATED_AT            TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
                             UPDATED_BY            VARCHAR(10)    NULL     COMMENT '수정자',
                             UPDATED_AT            TIMESTAMP      NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
                             PRIMARY KEY (GAME_ID),
                             KEY IDX_GAME_MASTER_STATUS (CREATION_STATUS_CODE),
                             KEY IDX_GAME_MASTER_CREATED_AT (CREATED_AT),
                             CONSTRAINT FK_GAME_MASTER_DIFFICULTY FOREIGN KEY (DIFFICULTY_LEVEL_CODE) REFERENCES COMMON_CODES(CODE_ID),
                             CONSTRAINT FK_GAME_MASTER_CREATION_STATUS FOREIGN KEY (CREATION_STATUS_CODE) REFERENCES COMMON_CODES(CODE_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='게임 마스터 정보 테이블';

-- 게임 상세 테이블
CREATE TABLE GAME_DETAIL (
                             GAME_ID        VARCHAR(10)    NOT NULL COMMENT '게임 ID',
                             GAME_SEQ       INT            NOT NULL COMMENT '게임 순번 (1, 2, 3...)',
                             GAME_ORDER     INT            NOT NULL COMMENT '게임 진행 순서',
                             CATEGORY_CODE  CHAR(6)        NOT NULL COMMENT '카테고리 코드 (가족/음식/여행/취미/일상/동물/자연)',
                             FILE_ID        INT            NOT NULL COMMENT '파일 ID (FILE_INFO FK)',
                             ANSWER_TEXT    VARCHAR(20)    NULL     COMMENT '정답 텍스트',
                             WRONG_OPTION_1 VARCHAR(20)    NULL     COMMENT '오답 선택지 1',
                             WRONG_OPTION_2 VARCHAR(20)    NULL     COMMENT '오답 선택지 2',
                             WRONG_OPTION_3 VARCHAR(20)    NULL     COMMENT '오답 선택지 3',
                             USER_ANSWER    VARCHAR(20)    NULL     COMMENT '사용자 답변',
                             IS_CORRECT     ENUM('Y', 'N') NOT NULL DEFAULT 'N' COMMENT '정답 여부',
                             ANSWER_TIME    TIMESTAMP      NULL     COMMENT '답변 시간',
                             CREATED_AT     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
                             PRIMARY KEY (GAME_ID, GAME_SEQ),
                             KEY IDX_GAME_DETAIL_CATEGORY (CATEGORY_CODE),
                             KEY IDX_GAME_DETAIL_ORDER (GAME_ORDER),
                             CONSTRAINT FK_GAME_DETAIL_MASTER FOREIGN KEY (GAME_ID) REFERENCES GAME_MASTER(GAME_ID),
                             CONSTRAINT FK_GAME_DETAIL_CATEGORY FOREIGN KEY (CATEGORY_CODE) REFERENCES COMMON_CODES(CODE_ID),
                             CONSTRAINT FK_GAME_DETAIL_FILE FOREIGN KEY (FILE_ID) REFERENCES FILE_INFO(FILE_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='게임 상세 정보 테이블 (개별 문제)';

-- 게임 플레이어 정답 테이블
CREATE TABLE GAME_PLAYER_ANSWER (
                                    GAME_ID         VARCHAR(10)    NOT NULL COMMENT '게임 ID',
                                    GAME_SEQ        INT            NOT NULL COMMENT '문제 순번',
                                    PLAYER_ID       VARCHAR(10)    NOT NULL COMMENT '플레이어 ID',
                                    SELECTED_OPTION INT            NOT NULL COMMENT '선택한 보기 번호 (1~4)',
                                    IS_CORRECT      ENUM('Y', 'N') NOT NULL COMMENT '정답 여부 (Y/N)',
                                    ANSWER_TIME_MS  INT            NULL     COMMENT '답변 소요 시간(ms)',
                                    SCORE_EARNED    INT            NULL     COMMENT '획득 점수',
                                    ANSWERED_AT     TIMESTAMP      NULL     COMMENT '답변 일시',
                                    PRIMARY KEY (GAME_ID, GAME_SEQ, PLAYER_ID),
                                    CONSTRAINT FK_GPA_GAME_DETAIL FOREIGN KEY (GAME_ID, GAME_SEQ) REFERENCES GAME_DETAIL(GAME_ID, GAME_SEQ),
                                    CONSTRAINT FK_GPA_PLAYER FOREIGN KEY (PLAYER_ID) REFERENCES USERS(USER_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='게임 플레이어별 정답 정보 테이블';

-- 게임 플레이어 테이블
CREATE TABLE GAME_PLAYER (
                             GAME_ID           VARCHAR(10)    NOT NULL COMMENT '게임 ID',
                             PLAYER_ID         VARCHAR(10)    NOT NULL COMMENT '플레이어 ID',
                             TOTAL_SCORE       INT            NULL     COMMENT '총 점수',
                             CORRECT_COUNT     INT            NULL     COMMENT '정답 개수',
                             ACCURACY_RATE     DECIMAL(5,2)   NULL     COMMENT '정답률',
                             GAME_STATUS_CODE  CHAR(6)        NOT NULL COMMENT '상태 코드',
                             START_TIME        TIMESTAMP      NULL     COMMENT '시작 시간',
                             END_TIME          TIMESTAMP      NULL     COMMENT '종료 시간',
                             DURATION_SECONDS  INT            NULL     COMMENT '소요 시간(초)',
                             PRIMARY KEY (GAME_ID, PLAYER_ID),
                             CONSTRAINT FK_GAME_PLAYER_GAME FOREIGN KEY (GAME_ID) REFERENCES GAME_MASTER(GAME_ID),
                             CONSTRAINT FK_GAME_PLAYER_PLAYER FOREIGN KEY (PLAYER_ID) REFERENCES USERS(USER_ID),
                             CONSTRAINT FK_GAME_PLAYER_STATUS FOREIGN KEY (GAME_STATUS_CODE) REFERENCES COMMON_CODES(CODE_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='게임별 플레이어 정보 테이블';

-- 뷰 생성
CREATE VIEW V_USER_INFO AS
SELECT
    u.USER_ID,
    u.USER_NAME,
    u.EMAIL,
    u.PHONE,
    u.USER_TYPE_CODE,
    ut.CODE_NAME as USER_TYPE_NAME,
    u.STATUS_CODE,
    us.CODE_NAME as STATUS_NAME,
    u.CREATED_AT,
    u.LOGIN_AT
FROM USERS u
         LEFT JOIN COMMON_CODES ut ON u.USER_TYPE_CODE = ut.CODE_ID
         LEFT JOIN COMMON_CODES us ON u.STATUS_CODE = us.CODE_ID;

-- 게임 정보 뷰 생성 (수정된 버전)
CREATE VIEW V_GAME_INFO AS
SELECT
    gm.GAME_ID,
    gm.GAME_NAME,
    gm.GAME_COUNT,
    gm.DIFFICULTY_LEVEL_CODE,
    dl.CODE_NAME as DIFFICULTY_LEVEL_NAME,
    gm.CREATION_STATUS_CODE,
    cs.CODE_NAME as CREATION_STATUS_NAME,
    gm.CREATED_BY,
    u.USER_NAME as CREATOR_NAME,
    gm.CREATED_AT,
    gm.UPDATED_AT
FROM GAME_MASTER gm
         LEFT JOIN COMMON_CODES dl ON gm.DIFFICULTY_LEVEL_CODE = dl.CODE_ID
         LEFT JOIN COMMON_CODES cs ON gm.CREATION_STATUS_CODE = cs.CODE_ID
         LEFT JOIN USERS u ON gm.CREATED_BY = u.USER_ID;

-- 외래키 체크 다시 활성화
SET FOREIGN_KEY_CHECKS = 1;


    -- =====================================================
-- MemoryForest MySQL Sample Data
-- 공통코드 샘플 데이터 (도메인별 구조: A-사용자, B-게임, C-시스템)
-- =====================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- 1. 사용자 도메인 (A)
-- =====================================================

-- 1.1. 사용자 도메인 루트
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY)
VALUES ('A00001', '사용자', NULL, 'ADMIN');

-- 1.1.1 사용자 유형 (USER_TYPE)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY)
VALUES ('A10001', '사용자 유형', 'A00001', 'ADMIN');

-- 1.1.2 하위 코드들
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('A20001', '환자', 'A10001', 'ADMIN'),
                                                                         ('A20002', '가족', 'A10001', 'ADMIN'),
                                                                         ('A20003', '관리자', 'A10001', 'ADMIN'),
                                                                         ('A20004', '의료진', 'A10001', 'ADMIN');

-- 1.2.1 계정 상태 (STATUS)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY)
VALUES ('A10002', '계정 상태', 'A00001', 'ADMIN');

-- 1.2.2 하위 코드들
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('A20005', '활성', 'A10002', 'ADMIN'),
                                                                         ('A20006', '비활성', 'A10002', 'ADMIN'),
                                                                         ('A20007', '정지', 'A10002', 'ADMIN'),
                                                                         ('A20008', '삭제', 'A10002', 'ADMIN'),
                                                                         ('A20009', '대기', 'A10002', 'ADMIN');

-- 1.3.1 가족 관계 (RELATIONSHIP)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY)
VALUES ('A10003', '가족 관계', 'A00001', 'ADMIN');

-- 1.3.2 하위 코드들
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('A20010', '배우자', 'A10003', 'ADMIN'),
                                                                         ('A20011', '아들', 'A10003', 'ADMIN'),
                                                                         ('A20012', '딸', 'A10003', 'ADMIN'),
                                                                         ('A20013', '손자', 'A10003', 'ADMIN'),
                                                                         ('A20014', '손녀', 'A10003', 'ADMIN'),
                                                                         ('A20015', '형제', 'A10003', 'ADMIN'),
                                                                         ('A20016', '자매', 'A10003', 'ADMIN'),
                                                                         ('A20017', '기타', 'A10003', 'ADMIN');

-- 1.4.1 연결 상태 (CONNECTION_STATUS)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY)
VALUES ('A10004', '연결 상태', 'A00001', 'ADMIN');

-- 1.4.2 하위 코드들
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('A20018', '연결됨', 'A10004', 'ADMIN'),
                                                                         ('A20019', '연결 대기', 'A10004', 'ADMIN'),
                                                                         ('A20020', '연결 해제', 'A10004', 'ADMIN'),
                                                                         ('A20021', '거부됨', 'A10004', 'ADMIN');

-- =====================================================
-- 2. 게임 도메인 (B)
-- =====================================================

-- 2.1. 게임 도메인 루트
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY)
VALUES ('B00001', '게임', NULL, 'ADMIN');

-- 2.1.1 게임 난이도 (DIFFICULTY_LEVEL)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY)
VALUES ('B10001', '게임 난이도', 'B00001', 'ADMIN');

-- 2.1.2 하위 코드들
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('B20001', '초급', 'B10001', 'ADMIN'),
                                                                         ('B20002', '중급', 'B10001', 'ADMIN'),
                                                                         ('B20003', '고급', 'B10001', 'ADMIN'),
                                                                         ('B20004', '전문가', 'B10001', 'ADMIN');

-- 2.2.1 게임 생성 상태 (CREATION_STATUS)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY)
VALUES ('B10002', '게임 생성 상태', 'B00001', 'ADMIN');

-- 2.2.2 하위 코드들
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('B20005', '대기중', 'B10002', 'ADMIN'),
                                                                         ('B20006', '생성중', 'B10002', 'ADMIN'),
                                                                         ('B20007', '완료', 'B10002', 'ADMIN'),
                                                                         ('B20008', '실패', 'B10002', 'ADMIN'),
                                                                         ('B20009', '취소', 'B10002', 'ADMIN');

-- 2.3.1 게임 진행 상태 (GAME_STATUS)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY)
VALUES ('B10003', '게임 진행 상태', 'B00001', 'ADMIN');

-- 2.3.2 하위 코드들
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('B20010', '대기', 'B10003', 'ADMIN'),
                                                                         ('B20011', '진행중', 'B10003', 'ADMIN'),
                                                                         ('B20012', '완료', 'B10003', 'ADMIN'),
                                                                         ('B20013', '중단', 'B10003', 'ADMIN'),
                                                                         ('B20014', '오류', 'B10003', 'ADMIN');

-- 2.4.1 게임 카테고리 (CATEGORY)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY)
VALUES ('B10004', '게임 카테고리', 'B00001', 'ADMIN');

-- 2.4.2. 1차 카테고리
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('B40001', '가족', 'B10004', 'ADMIN'),
                                                                         ('B40002', '음식', 'B10004', 'ADMIN'),
                                                                         ('B40003', '여행', 'B10004', 'ADMIN'),
                                                                         ('B40004', '취미', 'B10004', 'ADMIN'),
                                                                         ('B40005', '일상', 'B10004', 'ADMIN'),
                                                                         ('B40006', '동물', 'B10004', 'ADMIN'),
                                                                         ('B40007', '자연', 'B10004', 'ADMIN'),
                                                                         ('B40008', '기타', 'B10004', 'ADMIN');

-- 2.4.3. 2차 카테고리 (가족)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('B41001', '부모', 'B40001', 'ADMIN'),
                                                                         ('B41002', '자녀', 'B40001', 'ADMIN'),
                                                                         ('B41003', '배우자', 'B40001', 'ADMIN'),
                                                                         ('B41004', '손자녀', 'B40001', 'ADMIN'),
                                                                         ('B41005', '형제자매', 'B40001', 'ADMIN');

-- 2.4.4. 2차 카테고리 (음식)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('B42001', '한식', 'B40002', 'ADMIN'),
                                                                         ('B42002', '중식', 'B40002', 'ADMIN'),
                                                                         ('B42003', '일식', 'B40002', 'ADMIN'),
                                                                         ('B42004', '양식', 'B40002', 'ADMIN'),
                                                                         ('B42005', '디저트', 'B40002', 'ADMIN'),
                                                                         ('B42006', '음료', 'B40002', 'ADMIN');

-- 2.4.5. 2차 카테고리 (여행)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('B43001', '국내여행', 'B40003', 'ADMIN'),
                                                                         ('B43002', '해외여행', 'B40003', 'ADMIN'),
                                                                         ('B43003', '단체여행', 'B40003', 'ADMIN'),
                                                                         ('B43004', '가족여행', 'B40003', 'ADMIN');

-- 2.4.6. 2차 카테고리 (취미)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('B44001', '독서', 'B40004', 'ADMIN'),
                                                                         ('B44002', '운동', 'B40004', 'ADMIN'),
                                                                         ('B44003', '음악', 'B40004', 'ADMIN'),
                                                                         ('B44004', '미술', 'B40004', 'ADMIN'),
                                                                         ('B44005', '정원가꾸기', 'B40004', 'ADMIN'),
                                                                         ('B44006', '요리', 'B40004', 'ADMIN');

-- 2.4.7. 2차 카테고리 (일상)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('B45001', '집안일', 'B40005', 'ADMIN'),
                                                                         ('B45002', '쇼핑', 'B40005', 'ADMIN'),
                                                                         ('B45003', '의료', 'B40005', 'ADMIN'),
                                                                         ('B45004', '교통', 'B40005', 'ADMIN');

-- 2.4.8. 2차 카테고리 (동물)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('B46001', '반려동물', 'B40006', 'ADMIN'),
                                                                         ('B46002', '야생동물', 'B40006', 'ADMIN'),
                                                                         ('B46003', '조류', 'B40006', 'ADMIN'),
                                                                         ('B46004', '해양생물', 'B40006', 'ADMIN');

-- 2.4.9. 2차 카테고리 (자연)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('B47001', '산', 'B40007', 'ADMIN'),
                                                                         ('B47002', '바다', 'B40007', 'ADMIN'),
                                                                         ('B47003', '강', 'B40007', 'ADMIN'),
                                                                         ('B47004', '호수', 'B40007', 'ADMIN'),
                                                                         ('B47005', '꽃', 'B40007', 'ADMIN'),
                                                                         ('B47006', '나무', 'B40007', 'ADMIN');

-- =====================================================
-- 3. 시스템 도메인 (C)
-- =====================================================

-- 3.1. 시스템 도메인 루트
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY)
VALUES ('C00001', '시스템', NULL, 'ADMIN');

-- 3.1.1 히스토리 액션 타입 (ACTION_TYPE)
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY)
VALUES ('C10001', '히스토리 액션 타입', 'C00001', 'ADMIN');

-- 3.1.2 하위 코드들
INSERT INTO COMMON_CODES (CODE_ID, CODE_NAME, P_CODE_ID, CREATED_BY) VALUES
                                                                         ('C20001', '생성', 'C10001', 'ADMIN'),
                                                                         ('C20002', '수정', 'C10001', 'ADMIN'),
                                                                         ('C20003', '삭제', 'C10001', 'ADMIN'),
                                                                         ('C20004', '상태변경', 'C10001', 'ADMIN'),
                                                                         ('C20005', '로그인', 'C10001', 'ADMIN'),
                                                                         ('C20006', '로그아웃', 'C10001', 'ADMIN');

-- =====================================================
-- 4. 샘플 파일 데이터
-- =====================================================

-- 샘플 파일 정보
INSERT INTO FILE_INFO (ORIGINAL_NAME, S3_KEY, S3_URL, BUCKET_NAME, FILE_SIZE, CONTENT_TYPE, CREATED_BY, IS_PUBLIC) VALUES
                                                                                                                       ('family_photo1.jpg', 'games/images/family_photo1_20240717001.jpg', 'https://memoryforest-bucket.s3.amazonaws.com/games/images/family_photo1_20240717001.jpg', 'memoryforest-bucket', 1024000, 'image/jpeg', 'U0002', 'N'),
                                                                                                                       ('korean_food1.jpg', 'games/images/korean_food1_20240717002.jpg', 'https://memoryforest-bucket.s3.amazonaws.com/games/images/korean_food1_20240717002.jpg', 'memoryforest-bucket', 856000, 'image/jpeg', 'U0002', 'N'),
                                                                                                                       ('mountain1.jpg', 'games/images/mountain1_20240717003.jpg', 'https://memoryforest-bucket.s3.amazonaws.com/games/images/mountain1_20240717003.jpg', 'memoryforest-bucket', 1200000, 'image/jpeg', 'U0002', 'N'),
                                                                                                                       ('dog1.jpg', 'games/images/dog1_20240717004.jpg', 'https://memoryforest-bucket.s3.amazonaws.com/games/images/dog1_20240717004.jpg', 'memoryforest-bucket', 768000, 'image/jpeg', 'U0002', 'N'),
                                                                                                                       ('book1.jpg', 'games/images/book1_20240717005.jpg', 'https://memoryforest-bucket.s3.amazonaws.com/games/images/book1_20240717005.jpg', 'memoryforest-bucket', 512000, 'image/jpeg', 'U0002', 'N');

-- =====================================================
-- 5. 샘플 사용자 데이터
-- =====================================================

INSERT INTO USERS (USER_ID, USER_NAME, PASSWORD, EMAIL, PHONE, USER_TYPE_CODE, STATUS_CODE, CREATED_BY) VALUES
                                                                                                            ('U0001', '김철수', '$2a$10$example.hash', 'patient1@memoryforest.com', '010-1234-5678', 'A20001', 'A20005', 'ADMIN'),
                                                                                                            ('U0002', '이영희', '$2a$10$example.hash', 'family1@memoryforest.com', '010-2345-6789', 'A20002', 'A20005', 'ADMIN'),
                                                                                                            ('U0003', '박관리', '$2a$10$example.hash', 'admin@memoryforest.com', '010-3456-7890', 'A20003', 'A20005', 'ADMIN'),
                                                                                                            ('U0004', '최의사', '$2a$10$example.hash', 'doctor@memoryforest.com', '010-4567-8901', 'A20004', 'A20005', 'ADMIN');

-- =====================================================
-- 6. 샘플 사용자 관계 데이터
-- =====================================================

INSERT INTO USER_REL (PATIENT_ID, FAMILY_ID, RELATIONSHIP_CODE, STATUS_CODE) VALUES
    ('U0001', 'U0002', 'A20011', 'A20018');

-- =====================================================
-- 7. 샘플 게임 데이터
-- =====================================================

INSERT INTO GAME_MASTER (GAME_ID, GAME_NAME, GAME_DESC, GAME_COUNT, DIFFICULTY_LEVEL_CODE, CREATION_STATUS_CODE, CREATED_BY)
VALUES ('G250717001', '첫 번째 게임', '가족과 함께하는 기억력 게임', 5, 'B20001', 'B20007', 'U0002');

-- =====================================================
-- 8. 샘플 게임 플레이어 데이터
-- =====================================================

INSERT INTO GAME_PLAYER (GAME_ID, PLAYER_ID, TOTAL_SCORE, CORRECT_COUNT, ACCURACY_RATE, GAME_STATUS_CODE, START_TIME, END_TIME, DURATION_SECONDS)
VALUES
    ('G250717001', 'U0001', 80, 4, 80.00, 'B20012', '2024-07-17 10:00:00', '2024-07-17 10:10:00', 600);

-- =====================================================
-- 9. 샘플 게임 상세 데이터
-- =====================================================

INSERT INTO GAME_DETAIL (GAME_ID, GAME_SEQ, GAME_ORDER, CATEGORY_CODE, FILE_ID, ANSWER_TEXT, WRONG_OPTION_1, WRONG_OPTION_2, WRONG_OPTION_3) VALUES
                                                                                                                                                 ('G250717001', 1, 1, 'B41001', 1, '엄마', '아빠', '할머니', '할아버지'),
                                                                                                                                                 ('G250717001', 2, 2, 'B42001', 2, '김치찌개', '된장찌개', '순두부찌개', '부대찌개'),
                                                                                                                                                 ('G250717001', 3, 3, 'B47001', 3, '북한산', '남산', '관악산', '도봉산'),
                                                                                                                                                 ('G250717001', 4, 4, 'B46001', 4, '강아지', '고양이', '토끼', '햄스터'),
                                                                                                                                                 ('G250717001', 5, 5, 'B44001', 5, '책', '신문', '잡지', '노트');

-- =====================================================
-- 10. 샘플 게임 플레이어 정답 데이터
-- =====================================================

INSERT INTO GAME_PLAYER_ANSWER (GAME_ID, GAME_SEQ, PLAYER_ID, SELECTED_OPTION, IS_CORRECT, ANSWER_TIME_MS, SCORE_EARNED, ANSWERED_AT)
VALUES
    ('G250717001', 1, 'U0001', 1, 'Y', 5000, 20, '2024-07-17 10:01:00'),
    ('G250717001', 2, 'U0001', 1, 'Y', 6000, 20, '2024-07-17 10:02:00'),
    ('G250717001', 3, 'U0001', 2, 'N', 7000, 0, '2024-07-17 10:03:00'),
    ('G250717001', 4, 'U0001', 1, 'Y', 4000, 20, '2024-07-17 10:04:00'),
    ('G250717001', 5, 'U0001', 1, 'Y', 3000, 20, '2024-07-17 10:05:00');

-- 외래키 체크 다시 활성화
SET FOREIGN_KEY_CHECKS = 1;

-- 커밋
COMMIT;