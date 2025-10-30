# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI educational project that implements a REST API for managing ToDo items with MySQL database integration using SQLAlchemy ORM. The project follows a layered architecture pattern with clear separation between routes, data access, and database models.

## Development Commands

### Server
```bash
uvicorn main:app --reload
```
Run from the `src/` directory. The `--reload` flag enables hot reloading during development.

### Testing
```bash
pytest                    # Run all tests
pytest --cache-clear      # Clear pytest cache if issues occur
```

### Database Setup
```bash
# Start MySQL container
docker run -p 3306:3306 -e MYSQL_ROOT_PASSWORD=todos -e MYSQL_DATABASE=todos -d -v todos:/db --name todos mysql:8.0

# Access MySQL shell
docker exec -it todos bash
mysql -u root -p

# Create table (if not exists)
CREATE TABLE todo(
    id INT NOT NULL AUTO_INCREMENT,
    contents VARCHAR(256) NOT NULL,
    is_done BOOLEAN NOT NULL,
    PRIMARY KEY (id)
);
```

### Package Management (UV)
```bash
uv add <package>    # Add dependency
uv sync             # Install dependencies
```

## Architecture

### Layered Structure

The codebase follows a clean layered architecture:

**HTTP Layer** ([src/main.py](src/main.py))
- FastAPI route handlers
- Request/response orchestration
- Dependency injection via `Depends(get_db)`

**Schema Layer** ([src/schema/](src/schema/))
- `request.py`: Pydantic models for incoming requests
- `response.py`: Pydantic models for API responses with `from_attributes = True` for ORM compatibility

**Data Access Layer** ([src/database/repository.py](src/database/repository.py))
- Pure data access functions (no business logic)
- Functions: `get_todos()`, `get_todo_by_todo_id()`, `create_todo()`, `update_todo()`, `delete_todo()`

**ORM Layer** ([src/database/orm.py](src/database/orm.py))
- SQLAlchemy declarative models
- `ToDo` model with factory method `create()` and state methods `done()`/`undone()`

**Database Connection** ([src/database/connection.py](src/database/connection.py))
- SQLAlchemy engine and session factory
- `get_db()` generator for session lifecycle management
- Database URL: `mysql+pymysql://root:todos@127.0.0.1:3306/todos`

### Request Flow

```
HTTP Request
    ↓
Route Handler (main.py)
    ↓
Dependency Injection: get_db()
    ↓
Repository Function (repository.py)
    ↓
ORM Model (orm.py)
    ↓
SQLAlchemy → MySQL
    ↓
Pydantic Schema (response.py)
    ↓
JSON Response
```

### Key Patterns

**Dependency Injection**
- FastAPI's `Depends(get_db)` provides database sessions to route handlers
- Sessions are automatically closed via generator pattern

**ORM to Schema Conversion**
- Use `ToDoSchema.model_validate(todo)` to convert ORM objects to Pydantic models
- Requires `Config.from_attributes = True` in response schemas

**Session Management**
- Repository functions accept `Session` parameter
- For writes: `session.add()` → `session.commit()` → `session.refresh()`
- `session.refresh()` updates ORM object with database-generated values (e.g., auto-increment IDs)

## API Endpoints

All endpoints are defined in [src/main.py](src/main.py):

- `GET /` - Health check (returns `{"ping": "pong"}`)
- `GET /todos` - List all todos (optional `?order=DESC` query param)
- `GET /todos/{todo_id}` - Get single todo (404 if not found)
- `POST /todos` - Create new todo (201 status, auto-generates ID)
- `PATCH /todos/{todo_id}` - Update todo completion status (body: `{"is_done": bool}`)
- `DELETE /todos/{todo_id}` - Delete todo (204 status, 404 if not found)

## Testing

Tests use pytest with FastAPI's `TestClient`:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app=app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
```

Tests are located in [src/tests/](src/tests/) and follow `test_*.py` naming convention.

## Important Notes

- Python 3.12.9+ required
- Uses UV package manager (modern pip alternative)
- SQLAlchemy 2.0+ with modern query API (`select()` instead of legacy query API)
- Database credentials are hardcoded in [src/database/connection.py](src/database/connection.py:4)
- The `todo_data` dictionary in [src/main.py](src/main.py:22-38) is legacy code kept for reference (all handlers now use ORM)
- When working in this codebase, navigate to `src/` directory before running `uvicorn` or importing modules
