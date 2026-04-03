Here’s your README rewritten as clean, consistent Markdown. You can copy-paste this directly into `README.md` in your project root.

```markdown
# FastAPI CRUD API with PostgreSQL (Docker)

A simple CRUD backend service built with **Python**, **FastAPI**, **SQLAlchemy**, and **PostgreSQL** running in a **Docker container**.

## Architecture

- PostgreSQL runs in a **Docker container** (exposed on `localhost:5432`)
- FastAPI app runs on your **host machine** (e.g., macOS) inside a Python virtual environment
- The app connects to Postgres using SQLAlchemy and Pydantic v2 models

---

## Features

- RESTful CRUD API for an `Item` resource:
  - Create item
  - Read (list + detail)
  - Update item
  - Delete item
- PostgreSQL database (Docker)
- SQLAlchemy ORM for DB access
- Pydantic v2 schemas (`from_attributes` instead of `orm_mode`)
- Configuration via `pydantic-settings` (optional) and `.env`
- Auto-created tables on startup
- Interactive API documentation with Swagger UI (`/docs`)

---

## Tech Stack

- **Language**: Python 3.10+
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
- **Database**: PostgreSQL (Docker image `postgres:16`)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Settings Management**: [pydantic-settings](https://docs.pydantic.dev/latest/integrations/settings/)
- **OS**: macOS (but portable to Linux/Windows)

---

## Project Structure

Example layout:

```text
fastapi_postgres_docker_crud/
├─ venv/                        # Python virtual environment (not tracked in VCS)
├─ app/
│  ├─ __init__.py
│  ├─ main.py                   # FastAPI application entrypoint
│  ├─ api/
│  │  ├─ __init__.py
│  │  └─ v1/
│  │     ├─ __init__.py
│  │     ├─ routes_items.py     # CRUD routes for Item resource
│  │     └─ schemas.py          # Pydantic request/response models
│  ├─ core/
│  │  ├─ __init__.py
│  │  └─ config.py              # App & DB settings (BaseSettings)
│  └─ db/
│     ├─ __init__.py
│     ├─ base.py                # SQLAlchemy models (Item)
│     ├─ session.py             # Engine & SessionLocal
│     └─ deps.py                # DB dependency for FastAPI
├─ requirements.txt             # Python dependencies
├─ .env                         # Environment variables (optional)
└─ README.md
```

---

## Prerequisites

- **Docker Desktop** installed and running  
  Download: https://www.docker.com/products/docker-desktop
- **Python 3.10+** installed
- Basic familiarity with Terminal / command line

---

## 1. Start PostgreSQL in Docker

Run a PostgreSQL container:

```bash
docker run --name my_postgres \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=mycruddb \
  -p 5432:5432 \
  -d postgres:16
```

This will:

- Start a container named `my_postgres`
- Create database: `mycruddb`
- Create user: `myuser`
- Password: `mypassword`
- Expose Postgres on `localhost:5432`

Verify the container is running:

```bash
docker ps
```

You should see an entry with `postgres:16` and port mapping `0.0.0.0:5432->5432`.

---

## 2. Set Up Python Environment

From the project root (e.g., `fastapi_postgres_docker_crud/`):

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies (if `requirements.txt` exists):

```bash
pip install -r requirements.txt
```

If not, install manually:

```bash
pip install fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary pydantic pydantic-settings
pip freeze > requirements.txt
```

---

## 3. Configuration

Configuration is handled via a `Settings` class in `app/core/config.py`.

For Pydantic v2, `BaseSettings` comes from `pydantic-settings`:

```python
# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI CRUD with Docker Postgres"
    debug: bool = True

    # DB settings (must match Docker values)
    postgres_user: str = "myuser"
    postgres_password: str = "mypassword"
    postgres_server: str = "localhost"
    postgres_port: str = "5432"
    postgres_db: str = "mycruddb"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_server}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
```

### Optional: `.env` file

Create a `.env` file in the project root to override defaults:

```env
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mycruddb
APP_NAME="FastAPI CRUD with Docker Postgres"
DEBUG=true
```

`pydantic-settings` will automatically read from this file.

---

## 4. Database Setup

### 4.1. SQLAlchemy Engine and Session

```python
# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
```

### 4.2. Database Model

```python
# app/db/base.py
from sqlalchemy import Column, Integer, String, Float, Text
from app.db.session import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
```

### 4.3. DB Session Dependency

```python
# app/db/deps.py
from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Tables are created automatically when the app starts:

```python
# app/main.py (startup event)
from app.db.session import Base, engine


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
```

---

## 5. Pydantic Schemas (Pydantic v2)

```python
# app/api/v1/schemas.py
from typing import Optional
from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class ItemRead(ItemBase):
    id: int

    class Config:
        # Pydantic v2: replaces orm_mode = True
        from_attributes = True
```

---

## 6. CRUD Endpoints

CRUD endpoints are implemented in `app/api/v1/routes_items.py`:

```python
# app/api/v1/routes_items.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.schemas import ItemCreate, ItemUpdate, ItemRead
from app.db.deps import get_db
from app.db.base import Item as ItemModel

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=List[ItemRead])
def list_items(db: Session = Depends(get_db)):
    return db.query(ItemModel).all()


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = ItemModel(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.put("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
    return None
```

---

## 7. FastAPI Application Entrypoint

```python
# app/main.py
from fastapi import FastAPI
from app.api.v1.routes_items import router as items_router
from app.core.config import settings
from app.db.session import Base, engine

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


# Mount versioned API routes
app.include_router(items_router, prefix="/api/v1")
```

Run the app via Uvicorn from the command line; do not call `uvicorn.run()` inside `main.py`.

---

## 8. Running the Application

### 8.1. Ensure Docker Postgres is running

```bash
docker start my_postgres      # if it was stopped
docker ps                     # confirm it's up
```

### 8.2. Activate virtual environment

```bash
cd fastapi_postgres_docker_crud
source venv/bin/activate
```

### 8.3. Run the FastAPI app

```bash
uvicorn app.main:app --reload
```

You should see something like:

```text
Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 9. Testing the API

### 9.1. Health Check

- URL: `http://127.0.0.1:8000/health`
- Expected response:

```json
{ "status": "ok" }
```

### 9.2. Swagger UI (Interactive Docs)

- URL: `http://127.0.0.1:8000/docs`

From here you can interact with all endpoints:

- `GET /api/v1/items/` – list items
- `POST /api/v1/items/` – create new item
- `GET /api/v1/items/{item_id}` – get by ID
- `PUT /api/v1/items/{item_id}` – update
- `DELETE /api/v1/items/{item_id}` – delete

#### Example: Create an Item

In `/docs`, open `POST /api/v1/items/` and try:

```json
{
  "name": "Docker Test Item",
  "description": "Stored in Postgres container",
  "price": 49.99
}
```

---

## 10. Common Issues & Fixes

### 10.1. `BaseSettings` Import Error (Pydantic v2)

If you see:

> `pydantic.errors.PydanticImportError: BaseSettings has been moved to the pydantic-settings package`

Install and import from `pydantic-settings`:

```bash
pip install pydantic-settings
```

```python
from pydantic_settings import BaseSettings
```

### 10.2. `orm_mode` Warning in Pydantic v2

If you see a warning:

> `'orm_mode' has been renamed to 'from_attributes'`

Update your schema config:

```python
class Config:
    from_attributes = True
```

instead of:

```python
class Config:
    orm_mode = True
```

---

## 11. Next Steps / Possible Extensions

- Add **JWT authentication** and protect CRUD endpoints
- Add a **Dockerfile** and `docker-compose.yml` to run both API and DB as containers
- Use **Alembic** for database migrations
- Add **tests** using `pytest` and `httpx` or `TestClient`
- Implement pagination, filtering, and sorting for the `Item` list endpoint

---

## License

This project is intended for learning and internal/demo use.  
Feel free to adapt, extend, or integrate it into your own projects.
```

If you tell me your exact folder name (e.g., you changed it from `fastapi_postgres_docker_crud`), I can adjust the README paths and commands to match exactly.

Sources:

"# fastapi_postgres_docker_crud" 
