-- =====================================================
-- MemoryForest Database Schema for MySQL 8.0
-- AI 기반 치매 노인 인지훈련 서비스
-- =====================================================

-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS memory_forest CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE memory_forest;

-- 사용자 권한 설정
GRANT ALL PRIVILEGES ON memory_forest.* TO 'kcc'@'%';
FLUSH PRIVILEGES;


-- 공통코드 테이블
CREATE TABLE common_codes (
                              code_id         VARCHAR(6)     NOT NULL COMMENT '공통코드 ID (6자리 고정)',
                              code_name       VARCHAR(100)   NOT NULL COMMENT '공통코드명',
                              parent_code_id  VARCHAR(6)     NULL     COMMENT '부모 코드 ID (계층 구조)',
                              use_yn          VARCHAR(1)     NOT NULL DEFAULT 'Y' COMMENT '사용 여부',
                              created_by      VARCHAR(10)    NOT NULL COMMENT '생성자',
                              created_at      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
                              updated_by      VARCHAR(10)    NULL     COMMENT '수정자',
                              updated_at      TIMESTAMP      NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
                              PRIMARY KEY (code_id),
                              KEY idx_common_codes_parent_code_id (parent_code_id),
                              CONSTRAINT fk_common_codes_parent FOREIGN KEY (parent_code_id) REFERENCES common_codes(code_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='공통코드 관리 테이블 (계층적 구조)';

-- 파일 정보 테이블
CREATE TABLE file_info (
                           file_id         INT            NOT NULL AUTO_INCREMENT COMMENT '파일 ID (자동증가)',
                           original_name   VARCHAR(255)   NOT NULL COMMENT '원본 파일명',
                           s3_key          VARCHAR(500)   NOT NULL COMMENT 'S3 객체 키',
                           s3_url          VARCHAR(1000)  NOT NULL COMMENT 'S3 접근 URL',
                           bucket_name     VARCHAR(100)   NOT NULL COMMENT 'S3 버킷명',
                           file_size       BIGINT         NULL     COMMENT '파일 크기',
                           content_type    VARCHAR(100)   NULL     COMMENT '컨텐츠 타입',
                           upload_date     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '업로드일시',
                           created_by      VARCHAR(10)    NULL     COMMENT '생성자 ID',
                           is_public       VARCHAR(1)     NOT NULL DEFAULT 'N' COMMENT '공개/비공개 여부',
                           PRIMARY KEY (file_id),
                           UNIQUE KEY uk_s3_key (s3_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AWS S3 파일 정보 테이블';

-- 사용자 테이블
CREATE TABLE users (
                       user_id           VARCHAR(10)    NOT NULL COMMENT '사용자 ID (10자리)',
                       user_name         VARCHAR(100)   NOT NULL COMMENT '사용자명',
                       login_id          VARCHAR(100)   NOT NULL COMMENT '로그인 ID',
                       password          VARCHAR(60)    NULL COMMENT '암호화된 비밀번호 (OAuth 로그인 시 null 가능)',
                       email             VARCHAR(100)   NOT NULL COMMENT '이메일 (고유값)',
                       phone             VARCHAR(20)    NULL     COMMENT '전화번호',
                       birth_date        DATE           NULL     COMMENT '생년월일',
                       gender_code       VARCHAR(6)     NULL     COMMENT '성별 코드 (M/F)',
                       user_type_code    VARCHAR(6)     NOT NULL COMMENT '사용자 유형 코드 (환자/가족/관리자/의료진)',
                       login_type        VARCHAR(20)    NOT NULL DEFAULT 'DEFAULT' COMMENT '로그인 타입 (DEFAULT/NAVER/KAKAO)',
                       profile_image_file_id INT        NULL     COMMENT '프로필 이미지 파일 ID (FILE_INFO FK)',
                       status_code       VARCHAR(6)     NOT NULL COMMENT '계정 상태 코드 (활성/비활성/정지/삭제)',
                       created_by        VARCHAR(10)    NOT NULL COMMENT '생성자',
                       created_at        TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
                       updated_by        VARCHAR(10)    NULL     COMMENT '수정자',
                       updated_at        TIMESTAMP      NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
                       login_at          TIMESTAMP      NULL     COMMENT '마지막 로그인 일시',
                       PRIMARY KEY (user_id),
                       UNIQUE KEY uk_users_email (email),
                       KEY idx_users_user_type (user_type_code),
                       KEY idx_users_status (status_code),
                       CONSTRAINT fk_users_user_type FOREIGN KEY (user_type_code) REFERENCES common_codes(code_id),
                       CONSTRAINT fk_users_status FOREIGN KEY (status_code) REFERENCES common_codes(code_id),
                       CONSTRAINT fk_users_profile_image FOREIGN KEY (profile_image_file_id) REFERENCES file_info(file_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 정보 관리 테이블';

-- 사용자 관계 테이블
CREATE TABLE user_rel (
                          patient_id        VARCHAR(10)    NOT NULL COMMENT '환자 ID',
                          family_id         VARCHAR(10)    NOT NULL COMMENT '가족 ID',
                          relationship_code VARCHAR(6)     NOT NULL COMMENT '관계 코드 (배우자/아들/딸/손자/손녀/형제/자매)',
                          status_code       VARCHAR(6)     NOT NULL COMMENT '연결 상태 코드 (연결됨/연결대기/연결해제/거부됨)',
                          created_at        TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '관계 생성일시',
                          PRIMARY KEY (patient_id, family_id),
                          KEY idx_user_rel_patient (patient_id),
                          KEY idx_user_rel_family (family_id),
                          KEY idx_user_rel_status (status_code),
                          CONSTRAINT fk_user_rel_patient FOREIGN KEY (patient_id) REFERENCES users(user_id),
                          CONSTRAINT fk_user_rel_family FOREIGN KEY (family_id) REFERENCES users(user_id),
                          CONSTRAINT fk_user_rel_relationship FOREIGN KEY (relationship_code) REFERENCES common_codes(code_id),
                          CONSTRAINT fk_user_rel_status FOREIGN KEY (status_code) REFERENCES common_codes(code_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자 간 관계 정보 테이블 (환자-가족 연결)';

-- 게임 마스터 테이블
CREATE TABLE game_master (
                             game_id               VARCHAR(10)    NOT NULL COMMENT '게임 ID (G250717001 형식)',
                             game_name             VARCHAR(100)   NOT NULL COMMENT '게임명',
                             game_desc             VARCHAR(200)   NULL     COMMENT '게임 설명',
                             game_count            INT            NOT NULL COMMENT '게임 문제 수',
                             difficulty_level_code VARCHAR(6)     NOT NULL COMMENT '난이도 코드 (초급/중급/고급/전문가)',
                             creation_status_code  VARCHAR(6)     NOT NULL COMMENT '생성 상태 코드 (대기중/생성중/완료/실패/취소)',
                             created_by            VARCHAR(10)    NOT NULL COMMENT '생성자 (가족 또는 관리자)',
                             created_at            TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
                             updated_by            VARCHAR(10)    NULL     COMMENT '수정자',
                             updated_at            TIMESTAMP      NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
                             PRIMARY KEY (game_id),
                             KEY idx_game_master_status (creation_status_code),
                             KEY idx_game_master_created_at (created_at),
                             CONSTRAINT fk_game_master_difficulty FOREIGN KEY (difficulty_level_code) REFERENCES common_codes(code_id),
                             CONSTRAINT fk_game_master_creation_status FOREIGN KEY (creation_status_code) REFERENCES common_codes(code_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='게임 마스터 정보 테이블';

-- 게임 상세 테이블
CREATE TABLE game_detail (
                             game_id        VARCHAR(10)    NOT NULL COMMENT '게임 ID',
                             game_seq       INT            NOT NULL COMMENT '게임 순번 (1, 2, 3...)',
                             game_order     INT            NOT NULL COMMENT '게임 진행 순서',
                             game_title     VARCHAR(100)   NOT NULL COMMENT '게임 제목',
                             game_desc      VARCHAR(200)   NULL     COMMENT '게임 설명',
                             file_id        INT            NOT NULL COMMENT '파일 ID (FILE_INFO FK)',
                             answer_text    VARCHAR(20)    NULL     COMMENT '정답 텍스트',
                             wrong_option_1 VARCHAR(20)    NULL     COMMENT '오답 선택지 1',
                             wrong_option_2 VARCHAR(20)    NULL     COMMENT '오답 선택지 2',
                             wrong_option_3 VARCHAR(20)    NULL     COMMENT '오답 선택지 3',
                             wrong_score_1  INT            NULL     COMMENT '오답 점수 1',
                             wrong_score_2  INT            NULL     COMMENT '오답 점수 2',
                             wrong_score_3  INT            NULL     COMMENT '오답 점수 3',
                             ai_status_code VARCHAR(6)     NOT NULL COMMENT 'AI 상태 코드 (대기중/완료/실패)',
                             ai_processed_at TIMESTAMP     NULL     COMMENT 'AI 처리 일시',
                             description    VARCHAR(200)   NULL     COMMENT '문제 설명',
                             PRIMARY KEY (game_id, game_seq),
                             KEY idx_game_detail_order (game_order),
                             CONSTRAINT fk_game_detail_master FOREIGN KEY (game_id) REFERENCES game_master(game_id),
                             CONSTRAINT fk_game_detail_file FOREIGN KEY (file_id) REFERENCES file_info(file_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='게임 상세 정보 테이블 (개별 문제)';

-- 게임 플레이어 정답 테이블
CREATE TABLE game_player_answer (
                                    game_id         VARCHAR(10)    NOT NULL COMMENT '게임 ID',
                                    game_seq        INT            NOT NULL COMMENT '문제 순번',
                                    player_id       VARCHAR(10)    NOT NULL COMMENT '플레이어 ID',
                                    selected_option INT            NOT NULL COMMENT '선택한 보기 번호 (1~4)',
                                    is_correct      VARCHAR(1) NOT NULL     COMMENT '정답 여부 (Y/N)',
                                    answer_time_ms  INT            NULL     COMMENT '답변 소요 시간(ms)',
                                    score_earned    INT            NULL     COMMENT '획득 점수',
                                    answered_at     TIMESTAMP      NULL     COMMENT '답변 일시',
                                    PRIMARY KEY (game_id, game_seq, player_id),
                                    CONSTRAINT fk_gpa_game_detail FOREIGN KEY (game_id, game_seq) REFERENCES game_detail(game_id, game_seq),
                                    CONSTRAINT fk_gpa_player FOREIGN KEY (player_id) REFERENCES users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='게임 플레이어별 정답 정보 테이블';

-- 게임 플레이어 테이블
CREATE TABLE game_player (
                             game_id           VARCHAR(10)    NOT NULL COMMENT '게임 ID',
                             player_id         VARCHAR(10)    NOT NULL COMMENT '플레이어 ID',
                             total_score       INT            NULL     COMMENT '총 점수',
                             correct_count     INT            NULL     COMMENT '정답 개수',
                             accuracy_rate     DECIMAL(5,2)   NULL     COMMENT '정답률',
                             game_status_code  VARCHAR(6)     NOT NULL COMMENT '상태 코드',
                             start_time        TIMESTAMP      NULL     COMMENT '시작 시간',
                             end_time          TIMESTAMP      NULL     COMMENT '종료 시간',
                             duration_seconds  INT            NULL     COMMENT '소요 시간(초)',
                             PRIMARY KEY (game_id, player_id),
                             CONSTRAINT fk_game_player_game FOREIGN KEY (game_id) REFERENCES game_master(game_id),
                             CONSTRAINT fk_game_player_player FOREIGN KEY (player_id) REFERENCES users(user_id),
                             CONSTRAINT fk_game_player_status FOREIGN KEY (game_status_code) REFERENCES common_codes(code_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='게임별 플레이어 정보 테이블';


CREATE TABLE alarms (
                        alarm_id   INT AUTO_INCREMENT COMMENT '알람 ID',
                        player_id  VARCHAR(10)        NOT NULL COMMENT '플레이어 ID',
                        game_id    VARCHAR(10)        NOT NULL COMMENT '게임 ID',
                        is_read    VARCHAR(1) DEFAULT 'N' NOT NULL COMMENT '읽음 여부(Y/N)',
                        created_at TIMESTAMP           NOT NULL COMMENT '생성 일시',
                        PRIMARY KEY (alarm_id),
                        KEY idx_player_game (player_id, game_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='알람 테이블';

-- 녹음 기록 테이블
CREATE TABLE records (
                         record_id   INT           NOT NULL AUTO_INCREMENT COMMENT '녹음 기록 ID (자동증가)',
                         score       INT           NULL COMMENT '채점 점수',
                         user_id     VARCHAR(10)   NOT NULL COMMENT '사용자 ID',
                         file_id     INT           NULL COMMENT '파일 ID',
                         text        LONGTEXT      NULL COMMENT '녹음 텍스트',
                         duration    INT           NOT NULL COMMENT '녹음 시간(초 단위)',
                         created_at  TIMESTAMP     NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
                         PRIMARY KEY (record_id),
                         KEY idx_user_id (user_id),
                         KEY idx_file_id (file_id),
                         CONSTRAINT fk_records_user
                             FOREIGN KEY (user_id) REFERENCES users (user_id)
                                 ON DELETE CASCADE,
                         CONSTRAINT fk_records_file
                             FOREIGN KEY (file_id) REFERENCES file_info (file_id)
                                 ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='녹음 기록';

-- =====================================================
-- 1. 사용자 도메인 (A)
-- =====================================================

-- 1.1. 사용자 도메인 루트
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
VALUES ('A00001', '사용자', NULL, 'ADMIN');

-- 1.1.1 사용자 유형 (USER_TYPE)
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
VALUES ('A10001', '사용자 유형', 'A00001', 'ADMIN');

-- 1.1.2 하위 코드들
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
                                                                         ('A20001', '환자', 'A10001', 'ADMIN'),
                                                                         ('A20002', '가족', 'A10001', 'ADMIN'),
                                                                         ('A20003', '관리자', 'A10001', 'ADMIN'),
                                                                         ('A20004', '의료진', 'A10001', 'ADMIN');

-- 1.2.1 계정 상태 (STATUS)
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
VALUES ('A10002', '계정 상태', 'A00001', 'ADMIN');

-- 1.2.2 하위 코드들
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
                                                                         ('A20005', '활성', 'A10002', 'ADMIN'),
                                                                         ('A20006', '비활성', 'A10002', 'ADMIN'),
                                                                         ('A20007', '정지', 'A10002', 'ADMIN'),
                                                                         ('A20008', '삭제', 'A10002', 'ADMIN'),
                                                                         ('A20009', '대기', 'A10002', 'ADMIN');

-- 1.3.1 가족 관계 (RELATIONSHIP)
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
VALUES ('A10003', '가족 관계', 'A00001', 'ADMIN');

-- 1.3.2 하위 코드들
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
                                                                         ('A20010', '배우자', 'A10003', 'ADMIN'),
                                                                         ('A20011', '아들', 'A10003', 'ADMIN'),
                                                                         ('A20012', '딸', 'A10003', 'ADMIN'),
                                                                         ('A20013', '손자', 'A10003', 'ADMIN'),
                                                                         ('A20014', '손녀', 'A10003', 'ADMIN'),
                                                                         ('A20015', '형제', 'A10003', 'ADMIN'),
                                                                         ('A20016', '자매', 'A10003', 'ADMIN'),
                                                                         ('A20017', '기타', 'A10003', 'ADMIN');

-- 1.4.1 연결 상태 (CONNECTION_STATUS)
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
VALUES ('A10004', '연결 상태', 'A00001', 'ADMIN');

-- 1.4.2 하위 코드들
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
                                                                         ('A20018', '연결됨', 'A10004', 'ADMIN'),
                                                                         ('A20019', '연결 대기', 'A10004', 'ADMIN'),
                                                                         ('A20020', '연결 해제', 'A10004', 'ADMIN'),
                                                                         ('A20021', '거부됨', 'A10004', 'ADMIN');

-- 1.5.1 성별 (GENDER)
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
VALUES ('A10005', '성별', 'A00001', 'ADMIN');

-- 1.5.2 하위 코드들
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
                                                                         ('A20022', '남성', 'A10005', 'ADMIN'),
                                                                         ('A20023', '여성', 'A10005', 'ADMIN');

-- =====================================================
-- 2. 게임 도메인 (B)
-- =====================================================

-- 2.1. 게임 도메인 루트
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
VALUES ('B00001', '게임', NULL, 'ADMIN');

-- 2.1.1 게임 난이도 (DIFFICULTY_LEVEL)
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
VALUES ('B10001', '게임 난이도', 'B00001', 'ADMIN');

-- 2.1.2 하위 코드들
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
                                                                         ('B20001', '초급', 'B10001', 'ADMIN'),
                                                                         ('B20002', '중급', 'B10001', 'ADMIN'),
                                                                         ('B20003', '고급', 'B10001', 'ADMIN'),
                                                                         ('B20004', '전문가', 'B10001', 'ADMIN');

-- 2.2.1 게임 생성 상태 (CREATION_STATUS)
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
VALUES ('B10002', '게임 생성 상태', 'B00001', 'ADMIN');

-- 2.2.2 하위 코드들
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
                                                                         ('B20005', '대기중', 'B10002', 'ADMIN'),
                                                                         ('B20006', '생성중', 'B10002', 'ADMIN'),
                                                                         ('B20007', '완료', 'B10002', 'ADMIN'),
                                                                         ('B20008', '실패', 'B10002', 'ADMIN'),
                                                                         ('B20009', '취소', 'B10002', 'ADMIN');

-- 2.3.1 게임 진행 상태 (GAME_STATUS)
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
VALUES ('B10003', '게임 진행 상태', 'B00001', 'ADMIN');

-- 2.3.2 하위 코드들
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
                                                                         ('B20010', '대기', 'B10003', 'ADMIN'),
                                                                         ('B20011', '진행중', 'B10003', 'ADMIN'),
                                                                         ('B20012', '완료', 'B10003', 'ADMIN'),
                                                                         ('B20013', '중단', 'B10003', 'ADMIN'),
                                                                         ('B20014', '오류', 'B10003', 'ADMIN');

-- =====================================================
-- 3. 시스템 도메인 (C)
-- =====================================================

-- 3.1. 시스템 도메인 루트
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
VALUES ('C00001', '시스템', NULL, 'ADMIN');

-- 3.1.1 히스토리 액션 타입 (ACTION_TYPE)
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
VALUES ('C10001', '히스토리 액션 타입', 'C00001', 'ADMIN');

-- 3.1.2 하위 코드들
INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
                                                                         ('C20001', '생성', 'C10001', 'ADMIN'), 
                                                                         ('C20002', '수정', 'C10001', 'ADMIN'),
                                                                         ('C20003', '삭제', 'C10001', 'ADMIN'),
                                                                         ('C20004', '상태변경', 'C10001', 'ADMIN'),
                                                                         ('C20005', '로그인', 'C10001', 'ADMIN'),
                                                                         ('C20006', '로그아웃', 'C10001', 'ADMIN');

-- 외래키 체크 다시 활성화
SET FOREIGN_KEY_CHECKS = 1;

-- 커밋
COMMIT;