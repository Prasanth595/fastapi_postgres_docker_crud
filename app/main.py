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
    # Create tables in Docker Postgres if they don't exist
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


# Mount versioned API
app.include_router(items_router, prefix="/api/v1")