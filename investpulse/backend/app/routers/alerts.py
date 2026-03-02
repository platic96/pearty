import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models.alert import Alert
from app.models.alert_history import AlertHistory
from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate, BulkAlertAction
from app.schemas.alert_history import AlertHistoryPage, AlertHistoryWithAlert

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


# ─── Alert CRUD ──────────────────────────────────────────────

@router.get("", response_model=list[AlertResponse])
async def get_alerts(
    market: str | None = None,
    indicator: str | None = None,
    is_active: bool | None = None,
    session: AsyncSession = Depends(get_session),
):
    """알림 목록 조회 (필터 지원)."""
    query = select(Alert)
    if market:
        query = query.where(Alert.market == market)
    if indicator:
        query = query.where(Alert.indicator == indicator)
    if is_active is not None:
        query = query.where(Alert.is_active == is_active)
    query = query.order_by(Alert.created_at.desc())
    result = await session.execute(query)
    alerts = result.scalars().all()

    # trigger_count 계산
    responses = []
    for alert in alerts:
        count_result = await session.execute(
            select(func.count(AlertHistory.id)).where(AlertHistory.alert_id == alert.id)
        )
        count = count_result.scalar() or 0
        resp = AlertResponse.model_validate(alert)
        resp.trigger_count = count
        responses.append(resp)

    return responses


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
        cooldown_minutes=data.cooldown_minutes,
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return AlertResponse.model_validate(alert)


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
    return AlertResponse.model_validate(alert)


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


# ─── 복제 (Duplicate) ───────────────────────────────────────

@router.post("/{alert_id}/duplicate", response_model=AlertResponse)
async def duplicate_alert(
    alert_id: int, session: AsyncSession = Depends(get_session)
):
    """기존 알림 복제."""
    result = await session.execute(select(Alert).where(Alert.id == alert_id))
    original = result.scalar_one_or_none()
    if not original:
        raise HTTPException(status_code=404, detail="Alert not found")

    new_alert = Alert(
        market=original.market,
        indicator=original.indicator,
        condition=original.condition,
        threshold=original.threshold,
        cooldown_minutes=original.cooldown_minutes,
        is_active=False,
    )
    session.add(new_alert)
    await session.commit()
    await session.refresh(new_alert)
    return AlertResponse.model_validate(new_alert)


# ─── Bulk 작업 ───────────────────────────────────────────────

@router.post("/bulk", response_model=dict)
async def bulk_action(
    data: BulkAlertAction, session: AsyncSession = Depends(get_session)
):
    """다수 알림에 대한 일괄 작업 (활성화/비활성화/삭제)."""
    if not data.alert_ids:
        return {"affected": 0}

    if data.action == "delete":
        # 히스토리도 cascade 삭제됨
        await session.execute(
            delete(Alert).where(Alert.id.in_(data.alert_ids))
        )
        await session.commit()
        return {"affected": len(data.alert_ids), "action": "delete"}

    # activate / deactivate
    is_active = data.action == "activate"
    result = await session.execute(
        select(Alert).where(Alert.id.in_(data.alert_ids))
    )
    alerts = result.scalars().all()
    for alert in alerts:
        alert.is_active = is_active
    await session.commit()
    return {"affected": len(alerts), "action": data.action}


# ─── 히스토리 ────────────────────────────────────────────────

@router.get("/history", response_model=AlertHistoryPage)
async def get_all_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    market: str | None = None,
    indicator: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """전체 알림 히스토리 (페이지네이션)."""
    base_query = (
        select(AlertHistory)
        .join(Alert, AlertHistory.alert_id == Alert.id)
        .options(selectinload(AlertHistory.alert))
    )

    if market:
        base_query = base_query.where(Alert.market == market)
    if indicator:
        base_query = base_query.where(Alert.indicator == indicator)

    # 총 건수
    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    # 페이지 데이터
    data_query = (
        base_query
        .order_by(AlertHistory.triggered_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await session.execute(data_query)
    history_items = result.scalars().all()

    items = [
        AlertHistoryWithAlert(
            id=h.id,
            alert_id=h.alert_id,
            triggered_at=h.triggered_at,
            indicator_value=h.indicator_value,
            threshold=h.threshold,
            status=h.status,
            message=h.message,
            market=h.alert.market if h.alert else None,
            indicator=h.alert.indicator if h.alert else None,
            condition=h.alert.condition if h.alert else None,
        )
        for h in history_items
    ]

    return AlertHistoryPage(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )


@router.get("/{alert_id}/history", response_model=list[AlertHistoryWithAlert])
async def get_alert_history(
    alert_id: int,
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
):
    """특정 알림의 히스토리."""
    # 알림 존재 확인
    alert_result = await session.execute(select(Alert).where(Alert.id == alert_id))
    alert = alert_result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    result = await session.execute(
        select(AlertHistory)
        .where(AlertHistory.alert_id == alert_id)
        .order_by(AlertHistory.triggered_at.desc())
        .limit(limit)
    )
    history_items = result.scalars().all()

    return [
        AlertHistoryWithAlert(
            id=h.id,
            alert_id=h.alert_id,
            triggered_at=h.triggered_at,
            indicator_value=h.indicator_value,
            threshold=h.threshold,
            status=h.status,
            message=h.message,
            market=alert.market,
            indicator=alert.indicator,
            condition=alert.condition,
        )
        for h in history_items
    ]
