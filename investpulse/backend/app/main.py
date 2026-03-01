import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import alerts, indicators, market, portfolio
from app.routers import websocket as ws_router
from app.routers.market import _upbit_service
from app.routers.websocket import upbit_ws_relay
from app.services.alert_engine import AlertEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    # Alert Engine 시작
    alert_engine = AlertEngine(_upbit_service)
    alert_engine.start()

    # Upbit WebSocket 릴레이 백그라운드 태스크
    relay_task = asyncio.create_task(upbit_ws_relay())

    yield

    # Cleanup
    relay_task.cancel()
    alert_engine.shutdown()
    await _upbit_service.close()


app = FastAPI(title="InvestPulse API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(indicators.router)
app.include_router(alerts.router)
app.include_router(portfolio.router)
app.include_router(ws_router.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
