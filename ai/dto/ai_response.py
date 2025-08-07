# ai/dto/ai_response.py - MySQL 호환성 개선
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
    
    @field_validator('wrong_score_1', 'wrong_score_2', 'wrong_score_3', mode='before')
    @classmethod
    def convert_score_to_int(cls, v):
        """유사도 점수를 0-100 정수로 변환"""
        if v is None:
            return 0
        
        try:
            # numpy float, pandas float 등을 Python float로 변환
            if hasattr(v, 'item'):  # numpy 타입인 경우
                v = v.item()
            
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
                return max(0, min(100, score))
            else:
                logger.warning(f"예상하지 못한 점수 타입: {type(v)}, 값: {v}")
                return 0
                
        except Exception as e:
            logger.error(f"점수 변환 중 오류: {e}, 원본값: {v}, 타입: {type(v)}")
            return 0
    
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
        """초기화 후 응답 로깅"""
        logger.info(f"AI 응답 DTO 생성: game_id={self.game_id}, game_seq={self.game_seq}, "
                   f"ai_status={self.ai_status}")
        logger.info(f"AI 응답 결과: wrong_option_1='{self.wrong_option_1}', wrong_option_2='{self.wrong_option_2}', "
                   f"wrong_option_3='{self.wrong_option_3}'")
        logger.info(f"AI 응답 점수 (0-100): wrong_score_1={self.wrong_score_1}, wrong_score_2={self.wrong_score_2}, "
                   f"wrong_score_3={self.wrong_score_3}")
        logger.info(f"AI 응답 설명: {self.description}")

    def to_db_format(self) -> dict:
        """데이터베이스 저장용 형식으로 변환"""
        return {
            'wrong_option_1': self.wrong_option_1,
            'wrong_option_2': self.wrong_option_2,
            'wrong_option_3': self.wrong_option_3,
            'wrong_score_1': self.wrong_score_1,  # 이미 정수로 변환됨
            'wrong_score_2': self.wrong_score_2,
            'wrong_score_3': self.wrong_score_3,
            'ai_status': self.ai_status,
            'description': self.description
        }