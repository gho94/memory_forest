from pydantic import BaseModel, Field
from typing import Optional

class AIAnalysisRequest(BaseModel):
    game_id: str = Field(..., alias="gameId")
    game_seq: int = Field(..., alias="gameSeq")
    answer_text: str = Field(..., alias="answerText")
    difficulty_level: Optional[str] = Field("NORMAL", alias="difficultyLevel")  # 난이도 추가
         
    class Config:
        populate_by_name = True