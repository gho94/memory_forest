from pydantic import BaseModel, Field

class AIAnalysisRequest(BaseModel):
    game_id: str = Field(..., alias="gameId")
    game_seq: int = Field(..., alias="gameSeq") 
    answer_text: str = Field(..., alias="answerText")
    
    class Config:
        populate_by_name = True  