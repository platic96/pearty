from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


VALID_INDICATORS = Literal["RSI", "MACD", "BB", "PRICE", "CHANGE_RATE"]


class AlertCreate(BaseModel):
    market: str
    indicator: VALID_INDICATORS
    condition: str
    threshold: float
    cooldown_minutes: int = 30

    @field_validator("threshold")
    @classmethod
    def validate_threshold(cls, v: float, info) -> float:
        indicator = info.data.get("indicator")
        if indicator == "RSI" and not (0 <= v <= 100):
            raise ValueError("RSI threshold must be between 0 and 100")
        if indicator == "PRICE" and v <= 0:
            raise ValueError("PRICE threshold must be positive")
        if indicator == "CHANGE_RATE" and v <= 0:
            raise ValueError("CHANGE_RATE threshold must be positive (percentage)")
        return v

    @field_validator("cooldown_minutes")
    @classmethod
    def validate_cooldown(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Cooldown must be non-negative")
        return v


class AlertUpdate(BaseModel):
    market: str | None = None
    indicator: VALID_INDICATORS | None = None
    condition: str | None = None
    threshold: float | None = None
    is_active: bool | None = None
    cooldown_minutes: int | None = None


class AlertResponse(BaseModel):
    id: int
    market: str
    indicator: str
    condition: str
    threshold: float
    is_active: bool
    cooldown_minutes: int
    last_triggered_at: datetime | None
    trigger_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BulkAlertAction(BaseModel):
    alert_ids: list[int]
    action: Literal["activate", "deactivate", "delete"]
