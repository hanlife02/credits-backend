from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.training_program import TrainingProgram
from app.models.course_category import CourseCategory
from app.models.course import Course, GradingSystem
from app.schemas.dashboard import CreditSummary, CategoryProgress, CategoryProgressWithChildren

router = APIRouter()


@router.get("/credit-summary/{training_program_id}", response_model=CreditSummary)
def get_credit_summary(
    training_program_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get credit summary for a training program
    """
    # Check if training program exists
    training_program = db.query(TrainingProgram).filter(TrainingProgram.id == training_program_id).first()
    if not training_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training program not found",
        )

    # Check if user has access to this training program
    if not current_user.is_admin and training_program.user_id != current_user.id and not training_program.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Get all courses for this user
    user_courses = db.query(Course).filter(Course.user_id == current_user.id).all()

    # Calculate total earned credits and GPA
    total_earned_credits = 0.0
    weighted_gpa_sum = 0.0
    gpa_credits = 0.0

    for course in user_courses:
        # Only count courses that are passed or have a grade
        if (course.grading_system == GradingSystem.PASS_FAIL and course.passed) or \
           (course.grading_system == GradingSystem.PERCENTAGE and course.grade is not None):
            total_earned_credits += course.credits

            # Add to GPA calculation if it's a percentage-based course
            if course.grading_system == GradingSystem.PERCENTAGE and course.grade is not None:
                weighted_gpa_sum += course.gpa * course.credits
                gpa_credits += course.credits

    # Calculate overall GPA
    overall_gpa = round(weighted_gpa_sum / gpa_credits, 3) if gpa_credits > 0 else 0.0

    # Get all categories for this training program
    root_categories = db.query(CourseCategory).filter(
        CourseCategory.training_program_id == training_program_id,
        CourseCategory.parent_id == None,
    ).all()

    # Function to recursively calculate category progress
    def calculate_category_progress(category, user_courses):
        # Get all courses in this category
        category_courses = [c for c in user_courses if c.category_id == category.id]

        # Calculate earned credits for this category
        earned_credits = sum([
            c.credits for c in category_courses
            if (c.grading_system == GradingSystem.PASS_FAIL and c.passed) or
               (c.grading_system == GradingSystem.PERCENTAGE and c.grade is not None)
        ])

        # Get subcategories
        subcategories = db.query(CourseCategory).filter(
            CourseCategory.parent_id == category.id
        ).all()

        # Create progress object
        progress = CategoryProgressWithChildren(
            category_id=category.id,
            category_name=category.name,
            required_credits=category.required_credits,
            earned_credits=earned_credits,
            remaining_credits=max(0, category.required_credits - earned_credits),
            is_complete=earned_credits >= category.required_credits,
            has_subcategories=len(subcategories) > 0,
            parent_id=category.parent_id,
            subcategories=[]
        )

        # Calculate progress for subcategories
        for subcat in subcategories:
            subcat_progress = calculate_category_progress(subcat, user_courses)
            progress.subcategories.append(subcat_progress)

            # Add subcategory earned credits to parent category
            # earned_credits += subcat_progress.earned_credits

        return progress

    # Calculate progress for each root category
    categories_progress = [calculate_category_progress(cat, user_courses) for cat in root_categories]

    # Create credit summary
    credit_summary = CreditSummary(
        total_required_credits=training_program.total_credits,
        total_earned_credits=total_earned_credits,
        remaining_credits=max(0, training_program.total_credits - total_earned_credits),
        overall_gpa=overall_gpa,
        categories=categories_progress
    )

    return credit_summary
