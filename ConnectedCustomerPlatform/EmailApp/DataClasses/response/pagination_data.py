from typing import List, Any

from pydantic import BaseModel


class PaginationResponse(BaseModel):
    page_num: int
    total_entry_per_page: int
    total_entries: int
    total_pages: int
    data: List[Any]