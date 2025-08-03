from pydantic import BaseModel, Field
from typing import Optional

class AIAnalysisResponse(BaseModel):
    game_id: str = Field(..., alias="gameId")
    game_seq: int = Field(..., alias="gameSeq")
    wrong_option_1: str = Field(..., alias="wrongOption1")
    wrong_option_2: str = Field(..., alias="wrongOption2") 
    wrong_option_3: str = Field(..., alias="wrongOption3")
    similarity_score_1: float = Field(..., alias="similarityScore1")
    similarity_score_2: float = Field(..., alias="similarityScore2")
    similarity_score_3: float = Field(..., alias="similarityScore3")
    ai_status: str = Field(..., alias="aiStatus")
    description: Optional[str] = None
    
    class Config:
        populate_by_name = True