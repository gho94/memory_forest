# ai/dto/ai_response.py - 수정된 버전  
from pydantic import BaseModel, Field
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AIAnalysisResponse(BaseModel):
    game_id: str = Field(..., alias="gameId")
    game_seq: int = Field(..., alias="gameSeq")
    wrong_option_1: str = Field(default="", alias="wrongOption1")
    wrong_option_2: str = Field(default="", alias="wrongOption2") 
    wrong_option_3: str = Field(default="", alias="wrongOption3")
    wrong_score_1: float = Field(default=0.0, alias="wrongScore1")
    wrong_score_2: float = Field(default=0.0, alias="wrongScore2")
    wrong_score_3: float = Field(default=0.0, alias="wrongScore3")
    ai_status: str = Field(default="FAILED", alias="aiStatus")
    description: Optional[str] = Field(default="", alias="description")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
    
    def model_post_init(self, __context) -> None:
        """초기화 후 응답 로깅"""
        logger.info(f"AI 응답 DTO 생성: game_id={self.game_id}, game_seq={self.game_seq}, "
                   f"ai_status={self.ai_status}")
        logger.info(f"AI 응답 결과: wrong_option_1='{self.wrong_option_1}', wrong_option_2='{self.wrong_option_2}', "
                   f"wrong_option_3='{self.wrong_option_3}'")
        logger.info(f"AI 응답 점수: wrong_score_1={self.wrong_score_1}, wrong_score_2={self.wrong_score_2}, "
                   f"wrong_score_3={self.wrong_score_3}")
        logger.info(f"AI 응답 설명: {self.description}")