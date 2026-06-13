import json
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


# ---------- Auth ----------
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    avatar: str = ""

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    token: str
    user: UserOut
    session_id: str


class LoginRecordOut(BaseModel):
    id: int
    device: str
    title: str
    time: datetime
    location: str
    ip: str
    current: bool = False

    class Config:
        from_attributes = True


class LoginRecordListOut(BaseModel):
    items: list[LoginRecordOut]
    total: int


# ---------- Module ----------
class ModuleBase(BaseModel):
    name: str
    type: str = "业务模块"
    api_count: int = 0
    ui_count: int = 0
    perf_count: int = 0
    pass_rate: float = 0.0
    owner: str = ""


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(ModuleBase):
    pass


class ModuleOut(ModuleBase):
    id: int
    project_id: int
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- Member ----------
class MemberBase(BaseModel):
    name: str
    role: str = "测试工程师"
    email: str = ""


class MemberCreate(MemberBase):
    pass


class MemberOut(MemberBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True


# ---------- Project ----------
class ProjectBase(BaseModel):
    name: str
    code: str = ""
    status: str = "进行中"
    owner: str = "Admin"
    dept: str = "质量保障部"
    project_type: str = "Web + App + 后台"
    version: str = "V1.0.0"
    git_repo: str = ""
    description: str = ""


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectOut(ProjectBase):
    id: int
    created_at: datetime
    modules: list[ModuleOut] = []
    members: list[MemberOut] = []

    class Config:
        from_attributes = True


# ---------- API Case ----------
class ApiCaseBase(BaseModel):
    name: str
    method: str = "GET"
    url: str = ""
    module: str = ""
    priority: str = "中"
    status: str = "已启用"
    tags: str = ""
    params: str = ""
    headers: str = ""
    body: str = ""
    assertions: str = "[]"


class ApiCaseCreate(ApiCaseBase):
    pass


class ApiCaseUpdate(ApiCaseBase):
    pass


class ApiCaseOut(ApiCaseBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class ApiRunRequest(BaseModel):
    method: str = "GET"
    url: str = ""
    headers: str = ""
    body: str = ""
    assertions: str = "[]"


class ApiRunResponse(BaseModel):
    status_code: int
    status_text: str
    time_ms: int
    size: str
    body: str
    headers: dict
    assertions: list[dict]
    mocked: bool = False


# ---------- UI Case ----------
class UiStep(BaseModel):
    action: str = "点击"
    locator: str = ""
    value: str = ""
    desc: str = ""


class UiCaseBase(BaseModel):
    name: str
    module: str = ""
    browser: str = "Chrome"
    priority: str = "中"
    status: str = "未执行"
    creator: str = "Admin"
    steps: list[UiStep] = []


class UiCaseCreate(UiCaseBase):
    pass


class UiCaseUpdate(UiCaseBase):
    pass


class UiCaseOut(BaseModel):
    id: int
    name: str
    module: str
    browser: str
    priority: str
    status: str
    step_count: int
    creator: str
    steps: list[UiStep] = []
    updated_at: datetime

    @field_validator("steps", mode="before")
    @classmethod
    def parse_steps(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v or "[]")
            except json.JSONDecodeError:
                return []
        return v

    class Config:
        from_attributes = True


class UiRunLog(BaseModel):
    time: str
    step: str
    result: str
    cost: str


class UiRunResponse(BaseModel):
    status: str
    logs: list[UiRunLog]


# ---------- Test Plan ----------
class TestPlanBase(BaseModel):
    name: str
    type: str = "API / UI"
    env: str = "测试环境"
    status: str = "待执行"
    description: str = ""


class TestPlanCreate(TestPlanBase):
    pass


class TestPlanOut(TestPlanBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Dashboard ----------
class StatCard(BaseModel):
    key: str
    label: str
    value: str
    trend: float
    trend_label: str


class TrendPoint(BaseModel):
    date: str
    passed: int
    failed: int
    skipped: int


class ModulePassRate(BaseModel):
    name: str
    rate: float


class FailReason(BaseModel):
    name: str
    value: int


class PerfPoint(BaseModel):
    date: str
    avg: int
    p95: int
    p99: int


class ExecutionRecord(BaseModel):
    exec_id: str
    plan_name: str
    type: str
    env: str
    start_time: str
    status: str
    success_rate: float


class DashboardData(BaseModel):
    stats: list[StatCard]
    exec_trend: list[TrendPoint]
    module_pass_rate: list[ModulePassRate]
    fail_reasons: list[FailReason]
    perf_trend: list[PerfPoint]
    recent_executions: list[ExecutionRecord]
