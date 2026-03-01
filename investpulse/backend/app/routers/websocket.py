import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 클라이언트 연결 관리."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, data: dict) -> None:
        async with self._lock:
            dead: list[WebSocket] = []
            for conn in self.active_connections:
                try:
                    await conn.send_json(data)
                except Exception:
                    dead.append(conn)
            for d in dead:
                self.active_connections.remove(d)


manager = ConnectionManager()

# 기본 구독 마켓
DEFAULT_MARKETS = ["KRW-BTC", "KRW-ETH", "KRW-XRP", "KRW-SOL", "KRW-DOGE"]


async def upbit_ws_relay() -> None:
    """Upbit WebSocket에 연결하여 실시간 ticker 데이터를 모든 클라이언트에게 릴레이."""
    import websockets

    subscribe_msg = json.dumps([
        {"ticket": "investpulse-ticker"},
        {"type": "ticker", "codes": DEFAULT_MARKETS, "isOnlyRealtime": True},
    ])

    while True:
        try:
            async with websockets.connect("wss://api.upbit.com/websocket/v1") as ws:
                await ws.send(subscribe_msg)
                logger.info("Connected to Upbit WebSocket")

                while True:
                    raw = await ws.recv()
                    if isinstance(raw, bytes):
                        data = json.loads(raw.decode("utf-8"))
                    else:
                        data = json.loads(raw)

                    normalized = {
                        "market": data.get("code"),
                        "trade_price": data.get("trade_price"),
                        "signed_change_rate": data.get("signed_change_rate"),
                        "acc_trade_volume_24h": data.get("acc_trade_volume_24h"),
                        "trade_timestamp": data.get("trade_timestamp"),
                    }
                    await manager.broadcast(normalized)
        except Exception:
            logger.warning("Upbit WS disconnected, reconnecting in 5s...")
            await asyncio.sleep(5)


@router.websocket("/ws/market")
async def market_websocket(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
