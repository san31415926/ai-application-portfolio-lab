from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import chat, health, knowledge, models, notes


STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(
        title="LearningHub API",
        description="学习知识库、笔记、检索问答和回顾接口。",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(knowledge.router)
    app.include_router(chat.router)
    app.include_router(models.router)
    app.include_router(notes.router)
    app.mount("/app", StaticFiles(directory=STATIC_DIR, html=True), name="workbench")
    return app


app = create_app()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "LearningHub is running", "docs": "/docs", "workbench": "/app/"}
