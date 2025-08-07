# ai/dto/ai_request.py - 필드명 매핑 문제 해결
from pydantic import BaseModel, Field
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AIAnalysisRequest(BaseModel):
    # Java의 camelCase를 alias로 매핑
    game_id: str = Field(..., alias="gameId", description="게임 ID")
    game_seq: int = Field(..., alias="gameSeq", description="게임 시퀀스")
    answer_text: str = Field(..., alias="answerText", description="답변 텍스트")
    difficulty_level: Optional[str] = Field(default="NORMAL", alias="difficultyLevel", description="난이도 레벨")
    
    class Config:
        # alias와 field name 모두 허용
        populate_by_name = True
        # 추가 필드 허용하지 않음
        extra = 'forbid'
    
    def model_post_init(self, __context) -> None:
        """초기화 후 로깅"""
        logger.info(f"AI 요청 DTO 생성: game_id={self.game_id}, game_seq={self.game_seq}, "
                   f"answer_text='{self.answer_text}', difficulty_level={self.difficulty_level}")