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
