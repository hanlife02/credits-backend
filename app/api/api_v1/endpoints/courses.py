from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.training_program import TrainingProgram
from app.models.course_category import CourseCategory
from app.models.course import Course, GradingSystem
from app.schemas.course import (
    Course as CourseSchema,
    CourseCreate,
    CourseUpdate,
)

router = APIRouter()


@router.post("/", response_model=CourseSchema)
def create_course(
    course_in: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Create new course
    """
    # Check if category exists
    category = db.query(CourseCategory).filter(CourseCategory.id == course_in.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    # Check if user has access to the training program
    training_program = db.query(TrainingProgram).filter(TrainingProgram.id == category.training_program_id).first()
    if not current_user.is_admin and training_program.user_id != current_user.id and not training_program.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Validate grade based on grading system
    if course_in.grading_system == GradingSystem.PERCENTAGE:
        if course_in.grade is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Grade is required for percentage grading system",
            )
        if course_in.passed is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passed status should not be provided for percentage grading system",
            )
    elif course_in.grading_system == GradingSystem.PASS_FAIL:
        if course_in.passed is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passed status is required for pass/fail grading system",
            )
        if course_in.grade is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Grade should not be provided for pass/fail grading system",
            )
    
    # Create the course
    course = Course(
        **course_in.dict(),
        user_id=current_user.id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/", response_model=List[CourseSchema])
def read_courses(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Retrieve user's courses
    """
    courses = db.query(Course).filter(Course.user_id == current_user.id).offset(skip).limit(limit).all()
    return courses


@router.get("/{course_id}", response_model=CourseSchema)
def read_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific course by ID
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    
    # Check if user has permission to view this course
    if not current_user.is_admin and course.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return course


@router.put("/{course_id}", response_model=CourseSchema)
def update_course(
    course_id: str,
    course_in: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Update a course
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    
    # Check if user has permission to update this course
    if not current_user.is_admin and course.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # If category_id is being updated, check if it exists
    if course_in.category_id and course_in.category_id != course.category_id:
        category = db.query(CourseCategory).filter(CourseCategory.id == course_in.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
    
    # Update fields
    update_data = course_in.dict(exclude_unset=True)
    
    # Handle grading system changes
    if "grading_system" in update_data:
        new_grading_system = update_data["grading_system"]
        
        if new_grading_system == GradingSystem.PERCENTAGE:
            # If switching to percentage, ensure grade is provided and passed is removed
            if "grade" not in update_data and course.grade is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Grade is required for percentage grading system",
                )
            update_data["passed"] = None
        
        elif new_grading_system == GradingSystem.PASS_FAIL:
            # If switching to pass/fail, ensure passed is provided and grade is removed
            if "passed" not in update_data and course.passed is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Passed status is required for pass/fail grading system",
                )
            update_data["grade"] = None
    
    # Apply updates
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", response_model=dict)
def delete_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Delete a course
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    
    # Check if user has permission to delete this course
    if not current_user.is_admin and course.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}
