from datetime import datetime

from pydantic import BaseModel


class AlertHistoryResponse(BaseModel):
    id: int
    alert_id: int
    triggered_at: datetime
    indicator_value: float | None
    threshold: float
    status: str
    message: str | None

    model_config = {"from_attributes": True}


class AlertHistoryWithAlert(AlertHistoryResponse):
    """히스토리 항목 + 알림 기본 정보."""
    market: str | None = None
    indicator: str | None = None
    condition: str | None = None


class AlertHistoryPage(BaseModel):
    items: list[AlertHistoryWithAlert]
    total: int
    page: int
    size: int
    pages: int
