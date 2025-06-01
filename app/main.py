import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.route import pay, user

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

for uvicorn_logger in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    logging.getLogger(uvicorn_logger).handlers = logging.getLogger().handlers
    logging.getLogger(uvicorn_logger).setLevel(logging.INFO)

logger = logging.getLogger("app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting lifespan")
    await create_db_and_tables()
    yield
    logger.info("Stopping lifespan")

app = FastAPI(lifespan=lifespan)
app.include_router(user.router)
app.include_router(pay.router)

logger.info("Starting app")
