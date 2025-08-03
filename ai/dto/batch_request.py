from pydantic import BaseModel
from typing import Optional

class BatchProcessRequest(BaseModel):
    limit: Optional[int] = 10
