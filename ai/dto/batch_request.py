from pydantic import BaseModel
from typing import Optional

class BatchProcessRequest(BaseModel):
    limit: int = 50
    difficulty_filter: Optional[str] = None  # 특정 난이도만 처리하고 싶을 때