from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.training_program import TrainingProgram
from app.models.course_category import CourseCategory
from app.schemas.course_category import (
    CourseCategory as CourseCategorySchema,
    CourseCategoryCreate,
    CourseCategoryUpdate,
    CourseCategoryWithChildren,
)

router = APIRouter()


@router.post("/", response_model=CourseCategorySchema)
def create_course_category(
    category_in: CourseCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Create new course category
    """
    # Check if training program exists and user has access
    training_program = db.query(TrainingProgram).filter(TrainingProgram.id == category_in.training_program_id).first()
    if not training_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training program not found",
        )
    
    # Check if user has permission to add categories to this training program
    if not current_user.is_admin and training_program.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # If parent_id is provided, check if it exists and belongs to the same training program
    if category_in.parent_id:
        parent_category = db.query(CourseCategory).filter(
            CourseCategory.id == category_in.parent_id,
            CourseCategory.training_program_id == category_in.training_program_id,
        ).first()
        if not parent_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found or does not belong to the specified training program",
            )
    
    # Create the category
    category = CourseCategory(**category_in.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/training-program/{training_program_id}", response_model=List[CourseCategoryWithChildren])
def read_categories_by_training_program(
    training_program_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get all categories for a training program, organized in a tree structure
    """
    # Check if training program exists and user has access
    training_program = db.query(TrainingProgram).filter(TrainingProgram.id == training_program_id).first()
    if not training_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training program not found",
        )
    
    # Check if user has permission to view this training program
    if not current_user.is_admin and training_program.user_id != current_user.id and not training_program.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get all root categories (those without a parent)
    root_categories = db.query(CourseCategory).filter(
        CourseCategory.training_program_id == training_program_id,
        CourseCategory.parent_id == None,
    ).all()
    
    # Function to recursively build the category tree
    def build_category_tree(category):
        category_dict = CourseCategoryWithChildren.from_orm(category)
        subcategories = db.query(CourseCategory).filter(
            CourseCategory.parent_id == category.id
        ).all()
        category_dict.subcategories = [build_category_tree(subcat) for subcat in subcategories]
        return category_dict
    
    # Build the tree for each root category
    return [build_category_tree(category) for category in root_categories]


@router.get("/{category_id}", response_model=CourseCategorySchema)
def read_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific category by ID
    """
    category = db.query(CourseCategory).filter(CourseCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    # Check if user has permission to view this category
    training_program = db.query(TrainingProgram).filter(TrainingProgram.id == category.training_program_id).first()
    if not current_user.is_admin and training_program.user_id != current_user.id and not training_program.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return category


@router.put("/{category_id}", response_model=CourseCategorySchema)
def update_category(
    category_id: str,
    category_in: CourseCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Update a category
    """
    category = db.query(CourseCategory).filter(CourseCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    # Check if user has permission to update this category
    training_program = db.query(TrainingProgram).filter(TrainingProgram.id == category.training_program_id).first()
    if not current_user.is_admin and training_program.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Update fields
    update_data = category_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", response_model=dict)
def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Delete a category
    """
    category = db.query(CourseCategory).filter(CourseCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    # Check if user has permission to delete this category
    training_program = db.query(TrainingProgram).filter(TrainingProgram.id == category.training_program_id).first()
    if not current_user.is_admin and training_program.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Check if category has subcategories
    subcategories = db.query(CourseCategory).filter(CourseCategory.parent_id == category_id).count()
    if subcategories > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with subcategories",
        )
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}
