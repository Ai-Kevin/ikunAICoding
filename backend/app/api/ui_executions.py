from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import UiExecutionRecord, User
from app.schemas.schemas import (
    UiExecutionCreate,
    UiExecutionListResponse,
    UiExecutionOut,
    UiExecutionStatItem,
    UiExecutionStatsResponse,
)

router = APIRouter(prefix="/ui-executions", tags=["UI 执行记录"])


def _gen_task_id(start: datetime) -> str:
    return start.strftime("%Y%m%d%H%M%S") + f"{start.microsecond // 1000:03d}"


def _format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}秒"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}分{secs}秒" if secs else f"{minutes}分"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}小时{minutes}分"


@router.get("/stats", response_model=UiExecutionStatsResponse, summary="执行记录统计")
def execution_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    now = datetime.now()
    week_start = now - timedelta(days=7)
    prev_week_start = now - timedelta(days=14)

    total = db.query(func.count(UiExecutionRecord.id)).scalar() or 0
    success = (
        db.query(func.count(UiExecutionRecord.id))
        .filter(UiExecutionRecord.status == "成功")
        .scalar()
        or 0
    )
    failed = (
        db.query(func.count(UiExecutionRecord.id))
        .filter(UiExecutionRecord.status == "失败")
        .scalar()
        or 0
    )
    avg_duration = (
        db.query(func.avg(UiExecutionRecord.duration_seconds)).scalar() or 0
    )
    rate = round((success / total) * 100, 1) if total else 0.0

    def week_count(start: datetime, end: datetime) -> dict:
        rows = (
            db.query(
                func.count(UiExecutionRecord.id),
                func.sum(
                    case(
                        (UiExecutionRecord.status == "成功", 1),
                        else_=0,
                    )
                ),
                func.sum(
                    case(
                        (UiExecutionRecord.status == "失败", 1),
                        else_=0,
                    )
                ),
                func.avg(UiExecutionRecord.duration_seconds),
            )
            .filter(
                UiExecutionRecord.start_time >= start,
                UiExecutionRecord.start_time < end,
            )
            .first()
        )
        cnt = rows[0] or 0
        succ = rows[1] or 0
        fail = rows[2] or 0
        avg = rows[3] or 0
        week_rate = round((succ / cnt) * 100, 1) if cnt else 0.0
        return {"total": cnt, "success": succ, "failed": fail, "rate": week_rate, "avg": avg}

    cur = week_count(week_start, now)
    prev = week_count(prev_week_start, week_start)

    def trend(cur_val: float, prev_val: float, suffix: str = "", reverse: bool = False):
        diff = round(cur_val - prev_val, 1 if isinstance(cur_val, float) else 0)
        if reverse:
            up = diff <= 0
        else:
            up = diff >= 0
        sign = "+" if diff > 0 else ""
        text = f"{sign}{diff}{suffix}" if diff != 0 else "持平"
        return "较上周", text, up

    t_total = trend(cur["total"], prev["total"])
    t_success = trend(cur["success"], prev["success"])
    t_failed = trend(cur["failed"], prev["failed"])
    t_rate = trend(cur["rate"], prev["rate"], "%")
    t_avg = trend(round(cur["avg"]), round(prev["avg"]), "秒", reverse=True)

    return UiExecutionStatsResponse(
        stats=[
            UiExecutionStatItem(
                key="total",
                label="总执行次数",
                value=str(total),
                trend_label=t_total[0],
                trend_text=t_total[1],
                trend_up=t_total[2],
            ),
            UiExecutionStatItem(
                key="success",
                label="成功",
                value=str(success),
                trend_label=t_success[0],
                trend_text=t_success[1],
                trend_up=t_success[2],
            ),
            UiExecutionStatItem(
                key="failed",
                label="失败",
                value=str(failed),
                trend_label=t_failed[0],
                trend_text=t_failed[1],
                trend_up=not t_failed[2],
            ),
            UiExecutionStatItem(
                key="rate",
                label="成功率",
                value=f"{rate}%",
                trend_label=t_rate[0],
                trend_text=t_rate[1],
                trend_up=t_rate[2],
            ),
            UiExecutionStatItem(
                key="avg_duration",
                label="平均执行时长",
                value=_format_duration(int(avg_duration)),
                trend_label=t_avg[0],
                trend_text=t_avg[1],
                trend_up=t_avg[2],
            ),
        ]
    )


@router.get("", response_model=UiExecutionListResponse, summary="执行记录列表")
def list_executions(
    keyword: str | None = None,
    status: str | None = None,
    env: str | None = None,
    machine: str | None = None,
    creator: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(UiExecutionRecord)

    if keyword:
        like = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                UiExecutionRecord.task_id.like(like),
                UiExecutionRecord.name.like(like),
                UiExecutionRecord.creator.like(like),
            )
        )
    if status:
        query = query.filter(UiExecutionRecord.status == status)
    if env:
        query = query.filter(UiExecutionRecord.env == env)
    if machine:
        query = query.filter(UiExecutionRecord.machine == machine)
    if creator:
        query = query.filter(UiExecutionRecord.creator == creator)
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(UiExecutionRecord.start_time >= start)
        except ValueError:
            pass
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(UiExecutionRecord.start_time < end)
        except ValueError:
            pass

    total = query.count()
    items = (
        query.order_by(UiExecutionRecord.start_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return UiExecutionListResponse(items=items, total=total)


@router.get("/{record_id}", response_model=UiExecutionOut, summary="执行记录详情")
def get_execution(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    record = db.query(UiExecutionRecord).filter(UiExecutionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.post("", response_model=UiExecutionOut, summary="创建执行记录")
def create_execution(
    payload: UiExecutionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    end_time = payload.end_time or datetime.now()
    start_time = payload.start_time or (
        end_time - timedelta(seconds=payload.duration_seconds)
    )
    total = payload.total_cases
    rate = round((payload.success_count / total) * 100, 1) if total else 0.0
    status = "成功" if payload.fail_count == 0 else "失败"

    record = UiExecutionRecord(
        task_id=_gen_task_id(start_time),
        name=payload.name,
        env=payload.env,
        total_cases=payload.total_cases,
        success_count=payload.success_count,
        fail_count=payload.fail_count,
        skip_count=payload.skip_count,
        success_rate=rate,
        duration_seconds=payload.duration_seconds,
        machine=payload.machine,
        mode=payload.mode,
        creator=user.username,
        status=status,
        logs=payload.logs,
        start_time=start_time,
        end_time=end_time,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", summary="删除执行记录")
def delete_execution(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    record = db.query(UiExecutionRecord).filter(UiExecutionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}
