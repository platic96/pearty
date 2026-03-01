from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
async def get_alerts(
    market: str | None = None,
    is_active: bool | None = None,
    session: AsyncSession = Depends(get_session),
):
    """알림 목록 조회."""
    query = select(Alert)
    if market:
        query = query.where(Alert.market == market)
    if is_active is not None:
        query = query.where(Alert.is_active == is_active)
    query = query.order_by(Alert.created_at.desc())
    result = await session.execute(query)
    return result.scalars().all()


@router.post("", response_model=AlertResponse)
async def create_alert(
    data: AlertCreate, session: AsyncSession = Depends(get_session)
):
    """알림 생성."""
    alert = Alert(
        market=data.market,
        indicator=data.indicator,
        condition=data.condition,
        threshold=data.threshold,
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    data: AlertUpdate,
    session: AsyncSession = Depends(get_session),
):
    """알림 수정."""
    result = await session.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(alert, key, value)

    await session.commit()
    await session.refresh(alert)
    return alert


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int, session: AsyncSession = Depends(get_session)
):
    """알림 삭제."""
    result = await session.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await session.delete(alert)
    await session.commit()
    return {"status": "deleted", "id": alert_id}
