# ai/dto/ai_response.py - 안전한 문자열 처리 및 검증 강화
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

class AIAnalysisResponse(BaseModel):
    # Java가 기대하는 camelCase로 응답
    game_id: str = Field(..., alias="gameId", description="게임 ID")
    game_seq: int = Field(..., alias="gameSeq", description="게임 시퀀스")
    wrong_option_1: str = Field(default="", alias="wrongOption1", description="오답 선택지 1")
    wrong_option_2: str = Field(default="", alias="wrongOption2", description="오답 선택지 2")
    wrong_option_3: str = Field(default="", alias="wrongOption3", description="오답 선택지 3")
    wrong_score_1: int = Field(default=0, alias="wrongScore1", description="오답 점수 1 (0-100)")
    wrong_score_2: int = Field(default=0, alias="wrongScore2", description="오답 점수 2 (0-100)")
    wrong_score_3: int = Field(default=0, alias="wrongScore3", description="오답 점수 3 (0-100)")
    ai_status: str = Field(default="FAILED", alias="aiStatus", description="AI 처리 상태")
    description: Optional[str] = Field(default="", alias="description", description="처리 결과 설명")
    
    @field_validator('wrong_option_1', 'wrong_option_2', 'wrong_option_3', mode='before')
    @classmethod
    def validate_option_string(cls, v):
        """오답 선택지 문자열 검증 및 정리"""
        if v is None:
            return ""
        
        try:
            # 문자열로 변환
            if not isinstance(v, str):
                v = str(v)
            
            # 앞뒤 공백 제거
            v = v.strip()
            
            # 빈 문자열 처리
            if not v:
                return ""
            
            # 특수문자나 제어문자 제거 (필요시)
            # v = re.sub(r'[^\w\s가-힣]', '', v)  # 한글, 영문, 숫자, 공백만 허용
            
            # 길이 제한 (DB 필드 크기에 맞춰 조정)
            max_length = 255  # VARCHAR(255) 가정
            if len(v) > max_length:
                v = v[:max_length]
                logger.warning(f"선택지 길이 초과로 자름: {len(v)} -> {max_length}")
            
            logger.info(f"선택지 검증 완료: '{v}'")
            return v
            
        except Exception as e:
            logger.error(f"선택지 검증 중 오류: {e}, 원본값: {v}")
            return ""
    
    @field_validator('wrong_score_1', 'wrong_score_2', 'wrong_score_3', mode='before')
    @classmethod
    def convert_score_to_int(cls, v):
        """유사도 점수를 0-100 정수로 변환 (numpy array 지원)"""
        if v is None:
            return 0
        
        try:
            logger.info(f"점수 변환 시작: 값={v}, 타입={type(v)}")
            
            # numpy array인 경우 첫 번째 원소 추출
            if hasattr(v, 'shape') and len(v.shape) > 0:  # numpy array
                logger.info(f"numpy array 감지: shape={v.shape}")
                if len(v) > 0:
                    v = v[0]  # 첫 번째 원소
                else:
                    return 0
            
            # numpy scalar 타입인 경우 Python 타입으로 변환
            if hasattr(v, 'item'):  # numpy scalar
                logger.info(f"numpy scalar 감지: {type(v)}")
                v = v.item()
            
            # list인 경우 첫 번째 원소
            if isinstance(v, (list, tuple)) and len(v) > 0:
                logger.info(f"list/tuple 감지: {v}")
                v = v[0]
            
            logger.info(f"최종 변환 대상 값: {v}, 타입: {type(v)}")
            
            # float을 int로 변환 (0-1 범위를 0-100으로, 반올림)
            if isinstance(v, (float, int)):
                if 0 <= v <= 1:
                    # 0-1 범위의 유사도 점수를 0-100으로 변환
                    score = round(float(v) * 100)
                elif v > 1:
                    # 이미 0-100 범위인 경우 그대로 반올림
                    score = round(float(v))
                else:
                    # 음수인 경우 0으로
                    score = 0
                
                # 0-100 범위 제한
                final_score = max(0, min(100, score))
                logger.info(f"점수 변환 완료: {v} -> {final_score}")
                return final_score
            else:
                logger.warning(f"예상하지 못한 점수 타입: {type(v)}, 값: {v}")
                return 0
                
        except Exception as e:
            logger.error(f"점수 변환 중 오류: {e}, 원본값: {v}, 타입: {type(v)}", exc_info=True)
            return 0
    
    @field_validator('description', mode='before')
    @classmethod
    def validate_description(cls, v):
        """설명 문자열 검증"""
        if v is None:
            return ""
        
        try:
            if not isinstance(v, str):
                v = str(v)
            
            v = v.strip()
            
            # 설명 길이 제한
            max_length = 500  # 설명은 좀 더 길게 허용
            if len(v) > max_length:
                v = v[:max_length]
                logger.warning(f"설명 길이 초과로 자름: {len(v)} -> {max_length}")
            
            return v
            
        except Exception as e:
            logger.error(f"설명 검증 중 오류: {e}")
            return ""
    
    class Config:
        # alias와 field name 모두 허용
        populate_by_name = True
        # 응답 시 alias를 사용하도록 설정
        by_alias = True
        # 추가 필드 허용하지 않음
        extra = 'forbid'
        # JSON 인코딩 시 numpy 타입 처리
        json_encoders = {
            np.float32: lambda v: float(v),
            np.float64: lambda v: float(v),
            np.int32: lambda v: int(v),
            np.int64: lambda v: int(v),
        }
    
    def model_post_init(self, __context) -> None:
        """초기화 후 응답 로깅 및 검증"""
        logger.info(f"=== AI 응답 DTO 생성 ===")
        logger.info(f"game_id={self.game_id}, game_seq={self.game_seq}, ai_status={self.ai_status}")
        logger.info(f"wrong_option_1='{self.wrong_option_1}' (길이: {len(self.wrong_option_1)})")
        logger.info(f"wrong_option_2='{self.wrong_option_2}' (길이: {len(self.wrong_option_2)})")
        logger.info(f"wrong_option_3='{self.wrong_option_3}' (길이: {len(self.wrong_option_3)})")
        logger.info(f"wrong_score_1={self.wrong_score_1}, wrong_score_2={self.wrong_score_2}, wrong_score_3={self.wrong_score_3}")
        logger.info(f"description='{self.description}'")
        
        # 빈 선택지 경고
        if not self.wrong_option_1 and not self.wrong_option_2 and not self.wrong_option_3:
            logger.warning("⚠️ 모든 선택지가 비어있습니다!")
        
        # 데이터 일관성 체크
        if self.ai_status == "COMPLETED" and (not self.wrong_option_1 or not self.wrong_option_2 or not self.wrong_option_3):
            logger.warning("⚠️ COMPLETED 상태인데 일부 선택지가 비어있습니다!")

    def to_db_format(self) -> dict:
        """데이터베이스 저장용 형식으로 변환 (검증 강화)"""
        db_data = {
            'wrong_option_1': str(self.wrong_option_1) if self.wrong_option_1 else "",
            'wrong_option_2': str(self.wrong_option_2) if self.wrong_option_2 else "",
            'wrong_option_3': str(self.wrong_option_3) if self.wrong_option_3 else "",
            'wrong_score_1': int(self.wrong_score_1),
            'wrong_score_2': int(self.wrong_score_2),
            'wrong_score_3': int(self.wrong_score_3),
            'ai_status': str(self.ai_status),
            'description': str(self.description) if self.description else ""
        }
        
        logger.info(f"=== DB 형식 변환 완료 ===")
        for key, value in db_data.items():
            logger.info(f"{key}: '{value}' (타입: {type(value)}, 길이: {len(str(value)) if isinstance(value, str) else 'N/A'})")
        
        # 추가 검증: 빈 문자열 확인
        empty_options = [key for key, value in db_data.items() 
                        if key.startswith('wrong_option_') and not value]
        if empty_options:
            logger.warning(f"⚠️ DB 저장 시 빈 선택지 발견: {empty_options}")
        
        return db_data
    
    def validate_for_db(self) -> tuple[bool, str]:
        """DB 저장 전 유효성 검사"""
        issues = []
        
        # 필수 필드 확인
        if not self.game_id:
            issues.append("game_id가 비어있음")
        if self.game_seq is None:
            issues.append("game_seq가 None")
        
        # 선택지 확인
        options = [self.wrong_option_1, self.wrong_option_2, self.wrong_option_3]
        empty_count = sum(1 for opt in options if not opt)
        if empty_count == 3:
            issues.append("모든 선택지가 비어있음")
        elif empty_count > 0 and self.ai_status == "COMPLETED":
            issues.append(f"{empty_count}개 선택지가 비어있는데 COMPLETED 상태")
        
        # 점수 확인
        scores = [self.wrong_score_1, self.wrong_score_2, self.wrong_score_3]
        if any(score < 0 or score > 100 for score in scores):
            issues.append("점수가 0-100 범위를 벗어남")
        
        is_valid = len(issues) == 0
        message = "; ".join(issues) if issues else "검증 통과"
        
        logger.info(f"DB 유효성 검사: {'✅ 통과' if is_valid else '❌ 실패'} - {message}")
        
        return is_valid, message