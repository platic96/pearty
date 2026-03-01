from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class AlertCreate(BaseModel):
    market: str
    indicator: Literal["RSI", "MACD", "BB", "PRICE"]
    condition: str
    threshold: float


class AlertUpdate(BaseModel):
    market: str | None = None
    indicator: Literal["RSI", "MACD", "BB", "PRICE"] | None = None
    condition: str | None = None
    threshold: float | None = None
    is_active: bool | None = None


class AlertResponse(BaseModel):
    id: int
    market: str
    indicator: str
    condition: str
    threshold: float
    is_active: bool
    last_triggered_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
