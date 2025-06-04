from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from starlette.config import Config
from tortoise import Tortoise
from src.routes.users import users
from src.routes.chat import chat


config = Config('.env')

@asynccontextmanager
async def lifespan(app: FastAPI):
  try:
    await Tortoise.init(
      db_url=config("DB_URL"),
      modules={"models": ["src.models.users_model", "src.models.collections_model", "src.models.documents_model", "src.models.chat_history_model"]},
    )
    await Tortoise.generate_schemas()
    logging.info("DB initialized successfully")
    print("DB initialized successfully.")
    yield  # 서버가 이 시점에서 실행됨
  finally:
    await Tortoise.close_connections()
    print("DB shutdown complete.")

app = FastAPI(lifespan=lifespan)

app.include_router(users)
app.include_router(chat)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

# 로그 설정
logging.basicConfig(level=logging.INFO)
