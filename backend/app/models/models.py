from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), default="ADMIN")
    avatar = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    login_records = relationship(
        "LoginRecord", back_populates="user", cascade="all, delete-orphan"
    )


class LoginRecord(Base):
    __tablename__ = "login_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    session_id = Column(String(64), index=True, nullable=False)
    device = Column(String(16), default="desktop")
    title = Column(String(128), default="")
    ip = Column(String(64), default="")
    location = Column(String(128), default="")
    user_agent = Column(String(512), default="")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="login_records")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    code = Column(String(64), default="")
    status = Column(String(32), default="进行中")
    owner = Column(String(64), default="Admin")
    dept = Column(String(64), default="质量保障部")
    project_type = Column(String(64), default="Web + App + 后台")
    version = Column(String(32), default="V1.0.0")
    git_repo = Column(String(255), default="")
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    modules = relationship(
        "Module", back_populates="project", cascade="all, delete-orphan"
    )
    members = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String(128), nullable=False)
    type = Column(String(32), default="业务模块")
    api_count = Column(Integer, default=0)
    ui_count = Column(Integer, default=0)
    perf_count = Column(Integer, default=0)
    pass_rate = Column(Float, default=0.0)
    owner = Column(String(64), default="")
    updated_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="modules")


class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String(64), nullable=False)
    role = Column(String(32), default="测试工程师")
    email = Column(String(128), default="")

    project = relationship("Project", back_populates="members")


class ApiCase(Base):
    __tablename__ = "api_cases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    method = Column(String(16), default="GET")
    url = Column(String(255), default="")
    module = Column(String(64), default="")
    priority = Column(String(16), default="中")
    status = Column(String(16), default="已启用")
    tags = Column(String(255), default="")
    params = Column(Text, default="")
    headers = Column(Text, default='{\n  "Content-Type": "application/json"\n}')
    body = Column(Text, default="")
    assertions = Column(Text, default="[]")  # JSON list of {type, field, expect}
    updated_at = Column(DateTime, default=datetime.utcnow)


class UiCase(Base):
    __tablename__ = "ui_cases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    module = Column(String(64), default="")
    browser = Column(String(32), default="Chrome")
    priority = Column(String(16), default="中")
    status = Column(String(16), default="已通过")
    step_count = Column(Integer, default=0)
    creator = Column(String(64), default="Admin")
    steps = Column(Text, default="[]")  # JSON list of step dicts
    updated_at = Column(DateTime, default=datetime.utcnow)


class TestPlan(Base):
    __tablename__ = "test_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    type = Column(String(32), default="API / UI")
    env = Column(String(32), default="测试环境")
    status = Column(String(16), default="待执行")
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
