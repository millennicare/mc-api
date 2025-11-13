# mc-api

Millennicare API - A FastAPI-based REST API for connecting caregivers with careseekers.

## Description

This is the backend API for Millennicare, a platform that facilitates connections between caregivers and careseekers. The API provides comprehensive functionality for user management, authentication, appointment scheduling, payments, and various care service specialties including child care, senior care, housekeeping, pet care, and tutoring.

## What's in this repo

### Tech Stack

- **Framework**: FastAPI (with async/await support)
- **Python Version**: 3.13
- **Database**: PostgreSQL 18.0
- **ORM**: SQLAlchemy (async)
- **Migrations**: Alembic
- **Authentication**: JWT-based auth with Argon2 password hashing
- **Package Manager**: uv
- **Containerization**: Docker & Docker Compose

### Key Dependencies

- **fastapi** - Modern web framework for building APIs
- **sqlalchemy** - SQL toolkit and ORM
- **alembic** - Database migration tool
- **asyncpg** - Async PostgreSQL driver
- **pydantic** - Data validation using Python type annotations
- **pyjwt** - JSON Web Token implementation
- **argon2-cffi** - Secure password hashing
- **boto3** - AWS SDK (for S3 storage)
- **resend** - Email service integration
- **scalar-fastapi** - API documentation UI

## Getting Started

### Prerequisites

- (Python)[https://www.python.org/downloads/]
- (Docker)[https://www.docker.com/get-started/] OR (Orbstack)[https://orbstack.dev/]
- (uv)[https://docs.astral.sh/uv/getting-started/installation/]

### Environment variables

Run the following command to copy the environment variables and get the following variables from a team member.
```bash
cp .env.example .env
```
### Running the application

### With docker

**Note** Hot reload is not supported, this is simply to just run the service locally
```bash
# install dependencies
uv sync

# run the application
docker compose up
```

That's it, the migrations happen every time on startup.

## Local Development

```bash
# activate virtual environment with uv
uv venv

# install dependencies
uv sync

# create the database
docker compose up -d postgres

# run migrations
alembic upgrade head

# run the app
fastapi dev src/main.py
```
