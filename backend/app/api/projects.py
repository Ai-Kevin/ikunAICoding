from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import Module, Project, ProjectMember, User
from app.schemas.schemas import (
    MemberCreate,
    MemberOut,
    ModuleCreate,
    ModuleOut,
    ModuleUpdate,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["项目管理"])


def _get_project_or_404(db: Session, project_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


# ---------------- Project ----------------
@router.get("", response_model=list[ProjectOut], summary="项目列表")
def list_projects(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Project).all()


@router.get("/{project_id}", response_model=ProjectOut, summary="项目详情")
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return _get_project_or_404(db, project_id)


@router.post("", response_model=ProjectOut, summary="新建项目")
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.put("/{project_id}", response_model=ProjectOut, summary="编辑项目")
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    project = _get_project_or_404(db, project_id)
    for key, value in payload.model_dump().items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", summary="删除项目")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    project = _get_project_or_404(db, project_id)
    db.delete(project)
    db.commit()
    return {"message": "删除成功"}


# ---------------- Module ----------------
@router.post(
    "/{project_id}/modules", response_model=ModuleOut, summary="新建模块"
)
def create_module(
    project_id: int,
    payload: ModuleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id)
    module = Module(project_id=project_id, **payload.model_dump())
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


@router.put(
    "/{project_id}/modules/{module_id}",
    response_model=ModuleOut,
    summary="编辑模块",
)
def update_module(
    project_id: int,
    module_id: int,
    payload: ModuleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    module = (
        db.query(Module)
        .filter(Module.id == module_id, Module.project_id == project_id)
        .first()
    )
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    for key, value in payload.model_dump().items():
        setattr(module, key, value)
    module.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(module)
    return module


@router.delete(
    "/{project_id}/modules/{module_id}", summary="删除模块"
)
def delete_module(
    project_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    module = (
        db.query(Module)
        .filter(Module.id == module_id, Module.project_id == project_id)
        .first()
    )
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    db.delete(module)
    db.commit()
    return {"message": "删除成功"}


# ---------------- Member ----------------
@router.get(
    "/{project_id}/members",
    response_model=list[MemberOut],
    summary="成员列表",
)
def list_members(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id)
    return (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id)
        .all()
    )


@router.post(
    "/{project_id}/members", response_model=MemberOut, summary="添加成员"
)
def add_member(
    project_id: int,
    payload: MemberCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id)
    member = ProjectMember(project_id=project_id, **payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.delete(
    "/{project_id}/members/{member_id}", summary="移除成员"
)
def remove_member(
    project_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.id == member_id,
            ProjectMember.project_id == project_id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    db.delete(member)
    db.commit()
    return {"message": "移除成功"}
