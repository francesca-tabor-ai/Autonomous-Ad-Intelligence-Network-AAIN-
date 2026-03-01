from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from aain.main import bootstrap_system, SystemContext


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    system = await bootstrap_system()
    app.state.system = system
    yield
    await system.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(
        title="AAIN — Autonomous Ad Intelligence Network",
        version="0.1.0",
        description="Multi-agent ad decision system dashboard",
        lifespan=lifespan,
    )
    from aain.api.router import api_router
    app.include_router(api_router, prefix="/api/v1")
    return app
