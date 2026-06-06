from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import TestPlan, User
from app.schemas.schemas import TestPlanCreate, TestPlanOut

router = APIRouter(prefix="/test-plans", tags=["测试计划"])


@router.get("", response_model=list[TestPlanOut], summary="测试计划列表")
def list_plans(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(TestPlan).order_by(TestPlan.created_at.desc()).all()


@router.post("", response_model=TestPlanOut, summary="新建测试计划")
def create_plan(
    payload: TestPlanCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    plan = TestPlan(**payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}", summary="删除测试计划")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    plan = db.query(TestPlan).filter(TestPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    db.delete(plan)
    db.commit()
    return {"message": "删除成功"}
