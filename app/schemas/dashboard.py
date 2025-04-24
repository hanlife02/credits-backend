from typing import List, Optional
from pydantic import BaseModel


class CategoryProgress(BaseModel):
    category_id: str
    category_name: str
    required_credits: float
    earned_credits: float
    remaining_credits: float
    is_complete: bool
    has_subcategories: bool
    parent_id: Optional[str] = None


class CategoryProgressWithChildren(CategoryProgress):
    subcategories: List['CategoryProgressWithChildren'] = []


# Complete the recursive reference
CategoryProgressWithChildren.update_forward_refs()


class CreditSummary(BaseModel):
    total_required_credits: float
    total_earned_credits: float
    remaining_credits: float
    overall_gpa: float
    categories: List[CategoryProgressWithChildren]
