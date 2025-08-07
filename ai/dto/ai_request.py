# ai/dto/ai_request.py - 수정된 버전
from pydantic import BaseModel, Field
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AIAnalysisRequest(BaseModel):
    game_id: str = Field(..., alias="gameId")
    game_seq: int = Field(..., alias="gameSeq") 
    answer_text: str = Field(..., alias="answerText")
    difficulty_level: Optional[str] = Field("NORMAL", alias="difficultyLevel")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
    
    def model_post_init(self, __context) -> None:
        """초기화 후 로깅"""
        logger.info(f"AI 요청 DTO 생성: game_id={self.game_id}, game_seq={self.game_seq}, "
                   f"answer_text={self.answer_text}, difficulty_level={self.difficulty_level}")
