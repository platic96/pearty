from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AlertHistory(Base):
    __tablename__ = "alert_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), index=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    indicator_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String, default="triggered")  # triggered, sent, failed
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    alert: Mapped["Alert"] = relationship(back_populates="history")  # type: ignore[name-defined] # noqa: F821
