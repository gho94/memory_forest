from pydantic import BaseModel
from typing import Optional

class BatchProcessRequest(BaseModel):
    limit: int = 50
    difficulty_filter: Optional[str] = None 