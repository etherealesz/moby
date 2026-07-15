# FastAPI Backend Template

A FastAPI backend template with clean architecture, PostgreSQL integration, and comprehensive tooling setup.

## Data Flow Architecture

### Request Flow

### Incoming HTTP Request:

**Client**

⬇️ Sends request in **Pydantic Schema**

**Route Handler**

⬇️ Sends **Primitive Data Types** (`str`, `int`, etc.)

**Use Case Layer**

⬇️ Maps to **Application Domain Model**

**Repository Layer**

⬇️ Converts to **Database Model** (SQLAlchemy ORM)

**PostgreSQL Database**

### Response Flow:

**Database Query Result**

⬇️ Converts to **Database Model** (SQLAlchemy ORM)

**Repository Layer**

⬇️ Converts to **Application Domain Model**

**Use Case Layer**

⬇️ Forwards **Application Domain Model** from Repository Layer

**Router Handler**

⬇️ Converts to **Response Schema** (Pydantic)

**Client**

## Setup Instructions

### Prerequisites

- Python 3.14+
- PostgreSQL database
- Google Cloud Storage (optional)
- Docker (for containerized deployment)

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd template-be

# Install uv (Python package manager)
# For Linux and macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# For Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install dependencies (development mode)
uv sync --no-group deployment

# Install dependencies (production mode)
uv sync --no-dev --group deployment

# Activate virtual environment (Linux / MacOS)
source .venv/bin/activate

# Activate virtual environment (Windows)
.venv/Scripts/activate
```

### 2. Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install
```

### 3. Environment Variables

Setup the config files inside `files/config` directory depends on environment of the application (development, staging, production).

### 4. Database Setup (Optional)

```bash
# Run database migrations
alembic upgrade head

# Create new migration (when you modify models)
alembic revision --autogenerate -m "Description of changes"
```

### 5. Development Server

```bash
# Run development server
fastapi dev

# Or using uv
uv run fastapi dev
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Development Workflow

### Adding a New Module

1. **Create module structure**:

```bash
mkdir -p src/modules/your_module/{repositories,schemas,use_cases}
touch src/modules/your_module/{__init__.py,models.py,routers.py,exceptions.py}
```

2. **Define the entity** (`entity.py`):

```python
from sqlalchemy import Column, Integer, String
from infrastructures.databases.base import Base

class EntYourEntity(Base):
    __tablename__ = "your_table"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
```

> Note: Use Ent as prefix for entity classes to distinguish them.

3. **Define the domain model** (`models.py`):

```python
from pydantic import BaseModel

class MYourModel(BaseModel):
    id: int
    name: str
```

4. **Create repository** (`repositories/<data-source-name>_<domain_model_name>.py`):

```python
from fastapi_injector import inject
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_database_master_session

class YourRepository:
    @inject
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, model: MYourModel) -> MYourModel:
        # Implementation
        pass
```

5. **Implement use case** (`use_cases/your_use_case.py`):

```python
from fastapi import Depends
from fastapi_injector import inject
from .repositories.your_repository import YourRepository

class YourUseCase:
    @inject
    def __init__(self, repository: YourRepository):
        self.repository = repository

    async def execute(self, data):
        # Business logic implementation
        pass
```

> Note: Use case should be split per bussiness logic.

6. **Define schemas** (`schemas/request.py`, `schemas/response.py`):

```python
from pydantic import BaseModel

class SCreateRequest(BaseModel):
    name: str

class SYourResponse(BaseModel):
    id: int
    name: str
```

> Note: Use S as prefix for schema classes to distinguish them.

7. **Create router** (`routers.py`):

```python
from fastapi import APIRouter
from .use_cases.your_use_case import YourUseCase
from .schemas.request import CreateRequest
from .schemas.response import YourResponse
from fastapi_injector import Injected

router = APIRouter(prefix="/your-endpoint", tags=["Your Module"])

@router.post("", response_model=YourResponse)
async def create_item(
    body: CreateRequest,
    use_case: YourUseCase = Injected(YourUseCase)
):
    return await use_case.execute(body)
```

8. **Register router** in `src/app/routes.py`:

```python
from modules.your_module.routers import router as your_router
# Add to setup_routes function
api_router.include_router(your_router)
```

> Note: Uses import alias to avoid naming conflicts.

### Code Quality

```bash
# Run linting and formatting
uv run ruff check .
uv run ruff format .

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```
