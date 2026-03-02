from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    market: Mapped[str] = mapped_column(String, index=True)
    indicator: Mapped[str] = mapped_column(String)  # RSI, MACD, BB, PRICE, CHANGE_RATE
    condition: Mapped[str] = mapped_column(String)  # above, below, cross_up, cross_down
    threshold: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=30)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    history: Mapped[list["AlertHistory"]] = relationship(  # type: ignore[name-defined] # noqa: F821
        back_populates="alert", cascade="all, delete-orphan", order_by="desc(AlertHistory.triggered_at)"
    )
