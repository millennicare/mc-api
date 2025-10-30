# Testing Guide for Millennicare API

This document provides comprehensive guidance on testing the Millennicare API application.

## Table of Contents

- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Writing Tests](#writing-tests)
- [Best Practices](#best-practices)
- [Coverage](#coverage)

## Setup

### Install Test Dependencies

```bash
# Install test dependencies using uv
uv sync --group test
```

This will install:
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **httpx**: HTTP client for testing FastAPI
- **faker**: Generate fake test data

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only repository tests
pytest -m repository

# Run only service tests
pytest -m service

# Run only route/API tests
pytest -m route

# Run only auth-related tests
pytest -m auth
```

### Run Specific Test Files

```bash
# Test a specific file
pytest tests/unit/repositories/test_user_repository.py

# Test a specific class
pytest tests/unit/services/test_auth_service.py::TestAuthService

# Test a specific function
pytest tests/unit/repositories/test_user_repository.py::TestUserRepository::test_get_user_success
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage Report

```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Tests in Parallel (faster)

```bash
# Install pytest-xdist first
uv add --group test pytest-xdist

# Run tests in parallel
pytest -n auto
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── README.md                      # This file
└── unit/                          # Unit tests
    ├── __init__.py
    ├── repositories/              # Repository layer tests
    │   ├── __init__.py
    │   └── test_user_repository.py
    ├── services/                  # Service layer tests
    │   ├── __init__.py
    │   └── test_auth_service.py
    └── routes/                    # API endpoint tests
        ├── __init__.py
        └── test_auth_router.py
```

### Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests (isolated, fast)
- `@pytest.mark.integration` - Integration tests (database, external services)
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.repository` - Repository layer tests
- `@pytest.mark.service` - Service layer tests
- `@pytest.mark.route` - Route/API endpoint tests
- `@pytest.mark.auth` - Authentication related tests

## Writing Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Unit Test Structure

```python
import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.unit
@pytest.mark.repository
class TestUserRepository:
    """Test suite for UserRepository."""
    
    @pytest.fixture
    def repository(self, mock_db_session):
        """Create repository instance with mocked dependencies."""
        return UserRepository(db=mock_db_session)
    
    async def test_get_user_success(self, repository, sample_user_data):
        """Test successfully retrieving a user."""
        # Arrange - Set up test data and mocks
        user_id = sample_user_data["id"]
        mock_user = User(**sample_user_data)
        
        # Act - Execute the function being tested
        result = await repository.get_user(user_id=user_id)
        
        # Assert - Verify the results
        assert result is not None
        assert result.id == user_id
```

### Available Fixtures

Defined in `conftest.py`:

#### Database Fixtures
- `db_engine` - Test database engine (SQLite in-memory)
- `db_session` - Test database session
- `mock_db_session` - Mock database session for unit tests

#### Client Fixtures
- `client` - FastAPI TestClient
- `mock_email_client` - Mock email client
- `mock_jwt_client` - Mock JWT client

#### Sample Data Fixtures
- `sample_user_data` - Sample user data dictionary
- `sample_account_data` - Sample account data dictionary
- `sample_role_data` - Sample role data dictionary
- `sample_session_data` - Sample session data dictionary

### Testing Async Functions

```python
async def test_async_function(self, repository):
    """Test an async function."""
    result = await repository.some_async_method()
    assert result is not None
```

### Mocking Dependencies

```python
from unittest.mock import AsyncMock, MagicMock

async def test_with_mocks(self):
    """Test with mocked dependencies."""
    # Mock async method
    mock_repo = MagicMock()
    mock_repo.get_user = AsyncMock(return_value=mock_user)
    
    # Use the mock
    result = await mock_repo.get_user(user_id="123")
    
    # Verify mock was called
    mock_repo.get_user.assert_called_once_with(user_id="123")
```

### Testing Exceptions

```python
import pytest
from fastapi import HTTPException

async def test_raises_exception(self, service):
    """Test that function raises expected exception."""
    with pytest.raises(HTTPException) as exc_info:
        await service.some_method()
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail
```

## Best Practices

### 1. Follow AAA Pattern

Structure tests using Arrange-Act-Assert:

```python
async def test_example(self):
    # Arrange - Set up test data and mocks
    user_id = "123"
    
    # Act - Execute the function
    result = await repository.get_user(user_id)
    
    # Assert - Verify results
    assert result is not None
```

### 2. Test One Thing Per Test

Each test should verify a single behavior:

```python
# Good - Tests one specific scenario
async def test_get_user_success(self):
    """Test successfully retrieving a user."""
    pass

async def test_get_user_not_found(self):
    """Test user not found returns None."""
    pass

# Bad - Tests multiple scenarios
async def test_get_user(self):
    """Test get user."""
    # Tests both success and failure cases
    pass
```

### 3. Use Descriptive Test Names

Test names should clearly describe what is being tested:

```python
# Good
async def test_sign_in_fails_with_incorrect_password(self):
    pass

# Bad
async def test_sign_in(self):
    pass
```

### 4. Mock External Dependencies

Always mock external services (database, email, APIs):

```python
async def test_send_email(self, mock_email_client):
    """Test email sending without actually sending emails."""
    service = AuthService(email_client=mock_email_client)
    await service.send_verification_email("test@example.com")
    mock_email_client.send_verification_email.assert_called_once()
```

### 5. Use Fixtures for Common Setup

Define reusable fixtures in `conftest.py`:

```python
@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(id="123", email="test@example.com", name="Test User")
```

### 6. Test Edge Cases

Test boundary conditions and error scenarios:

```python
async def test_get_users_empty_list(self):
    """Test getting users when database is empty."""
    pass

async def test_create_user_with_duplicate_email(self):
    """Test creating user with existing email fails."""
    pass

async def test_update_user_with_invalid_id(self):
    """Test updating non-existent user raises error."""
    pass
```

### 7. Keep Tests Independent

Each test should be able to run independently:

```python
# Good - Each test sets up its own data
async def test_create_user(self):
    user_data = {"name": "Test", "email": "test@example.com"}
    result = await repository.create_user(user_data)
    assert result is not None

# Bad - Depends on previous test
async def test_get_created_user(self):
    # Assumes user from previous test exists
    result = await repository.get_user("123")
```

## Coverage

### View Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html
```

### Coverage Goals

- **Overall**: Aim for 80%+ coverage
- **Critical paths**: 90%+ coverage for auth, payment, core business logic
- **Repositories**: 85%+ coverage
- **Services**: 85%+ coverage
- **Routes**: 75%+ coverage

### Check Coverage in CI/CD

```bash
# Fail if coverage is below 80%
pytest --cov=src --cov-fail-under=80
```

## Testing Layers

### Repository Layer Tests

Focus on database operations:

```python
async def test_repository_method(self, repository, mock_db_session):
    """Test repository database interaction."""
    # Mock database response
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result
    
    # Test repository method
    result = await repository.get_user(user_id="123")
    
    # Verify database was called correctly
    mock_db_session.execute.assert_called_once()
```

### Service Layer Tests

Focus on business logic:

```python
async def test_service_method(self, auth_service, mock_user_repository):
    """Test service business logic."""
    # Mock repository responses
    mock_user_repository.get_user_by_email = AsyncMock(return_value=None)
    
    # Test service method
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.sign_in("test@example.com", "password")
    
    # Verify correct exception
    assert exc_info.value.status_code == 401
```

### Route Layer Tests

Focus on API endpoints:

```python
def test_endpoint(self, client):
    """Test API endpoint."""
    # Make request
    response = client.post("/api/auth/sign-up", json={
        "name": "Test",
        "email": "test@example.com",
        "password": "password123"
    })
    
    # Verify response
    assert response.status_code == 201
    assert "id" in response.json()
```

## Continuous Integration

Tests should run automatically on:
- Pull requests
- Commits to main branch
- Before deployment

Example GitHub Actions workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --group test
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Tests Fail Due to Database Connection

Make sure you're using the in-memory SQLite database for tests, not the production database.

### Async Tests Not Running

Ensure `pytest-asyncio` is installed and `asyncio_mode = auto` is set in `pytest.ini`.

### Import Errors

Make sure the project root is in your Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Fixtures Not Found

Ensure `conftest.py` is in the correct location and fixtures are properly defined.

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
