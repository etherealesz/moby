from typing import Dict, List
from pydantic import BaseModel


class DBulkOperationResultMeta(BaseModel):
    total_count: int
    success_count: int
    failure_count: int
    errors: Dict[str, List[str]]
