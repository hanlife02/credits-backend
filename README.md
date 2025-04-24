# Graduation Credit Audit System Backend

A backend API for managing graduation credits and requirements.

## Features

- Email authentication with verification codes
- User roles (regular users and admin users)
- Training program management
- Course category management with hierarchical structure
- Course management with different grading systems
- Dashboard for tracking progress toward graduation requirements

## Setup

### Prerequisites

- Python 3.8+

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd credits-backend
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

5. Edit the `.env` file with your configuration.

6. Initialize the database:

```bash
alembic upgrade head
```

### Running the Application

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000.

API documentation will be available at http://localhost:8000/docs.

## API Endpoints

### Authentication

- `POST /api/v1/auth/register/request` - Request email verification for registration
- `POST /api/v1/auth/register/confirm` - Complete registration with verification code
- `POST /api/v1/auth/login` - Login and get access token
- `POST /api/v1/auth/password-reset/request` - Request password reset
- `POST /api/v1/auth/password-reset/confirm` - Confirm password reset with verification code

### Users

- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/{user_id}` - Get a specific user by ID (admin only)

### Training Programs

- `POST /api/v1/training-programs/` - Create a new training program
- `GET /api/v1/training-programs/` - Get all training programs
- `GET /api/v1/training-programs/{training_program_id}` - Get a specific training program
- `PUT /api/v1/training-programs/{training_program_id}` - Update a training program
- `DELETE /api/v1/training-programs/{training_program_id}` - Delete a training program
- `POST /api/v1/training-programs/{training_program_id}/publish` - Publish a training program (admin only)

### Course Categories

- `POST /api/v1/course-categories/` - Create a new course category
- `GET /api/v1/course-categories/training-program/{training_program_id}` - Get all categories for a training program
- `GET /api/v1/course-categories/{category_id}` - Get a specific category
- `PUT /api/v1/course-categories/{category_id}` - Update a category
- `DELETE /api/v1/course-categories/{category_id}` - Delete a category

### Courses

- `POST /api/v1/courses/` - Create a new course
- `GET /api/v1/courses/` - Get all courses for the current user
- `GET /api/v1/courses/{course_id}` - Get a specific course
- `PUT /api/v1/courses/{course_id}` - Update a course
- `DELETE /api/v1/courses/{course_id}` - Delete a course

### Dashboard

- `GET /api/v1/dashboard/credit-summary/{training_program_id}` - Get credit summary for a training program

### Health Check

- `GET /health` - Check if the API is running

## API Key

All API requests require an API key to be included in the `X-API-Key` header.
