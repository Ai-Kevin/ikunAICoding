from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import (
    DashboardData,
    ExecutionRecord,
    FailReason,
    ModulePassRate,
    PerfPoint,
    StatCard,
    TrendPoint,
)

router = APIRouter(prefix="/dashboard", tags=["工作台"])


@router.get("", response_model=DashboardData, summary="工作台概览数据")
def dashboard(_: User = Depends(get_current_user)):
    return DashboardData(
        stats=[
            StatCard(key="api", label="API 用例数", value="1,284", trend=12.5, trend_label="较上周"),
            StatCard(key="ui", label="UI 用例数", value="326", trend=8.3, trend_label="较上周"),
            StatCard(key="perf", label="性能脚本数", value="89", trend=5.6, trend_label="较上周"),
            StatCard(key="exec", label="今日执行次数", value="42", trend=16.7, trend_label="较昨日"),
            StatCard(key="rate", label="成功率", value="96.8%", trend=2.3, trend_label="较昨日"),
            StatCard(key="fail", label="失败缺陷数", value="17", trend=-5.6, trend_label="较昨日"),
        ],
        exec_trend=[
            TrendPoint(date="05-22", passed=62, failed=20, skipped=8),
            TrendPoint(date="05-23", passed=70, failed=22, skipped=10),
            TrendPoint(date="05-24", passed=66, failed=18, skipped=7),
            TrendPoint(date="05-25", passed=72, failed=24, skipped=9),
            TrendPoint(date="05-26", passed=78, failed=21, skipped=11),
            TrendPoint(date="05-27", passed=82, failed=25, skipped=8),
            TrendPoint(date="05-28", passed=90, failed=23, skipped=12),
        ],
        module_pass_rate=[
            ModulePassRate(name="用户模块", rate=98.6),
            ModulePassRate(name="订单模块", rate=96.3),
            ModulePassRate(name="支付模块", rate=94.2),
            ModulePassRate(name="商品模块", rate=97.8),
            ModulePassRate(name="优惠模块", rate=93.1),
            ModulePassRate(name="后台管理", rate=95.4),
        ],
        fail_reasons=[
            FailReason(name="断言失败", value=24),
            FailReason(name="接口错误", value=14),
            FailReason(name="超时", value=9),
            FailReason(name="数据不一致", value=5),
            FailReason(name="其他", value=5),
        ],
        perf_trend=[
            PerfPoint(date="05-22", avg=1100, p95=1700, p99=2050),
            PerfPoint(date="05-23", avg=950, p95=1500, p99=1850),
            PerfPoint(date="05-24", avg=1000, p95=1600, p99=1950),
            PerfPoint(date="05-25", avg=880, p95=1450, p99=1800),
            PerfPoint(date="05-26", avg=920, p95=1500, p99=1880),
            PerfPoint(date="05-27", avg=1050, p95=1650, p99=2000),
            PerfPoint(date="05-28", avg=900, p95=1480, p99=1900),
        ],
        recent_executions=[
            ExecutionRecord(exec_id="#20240528001", plan_name="每日回归测试", type="API / UI", env="测试环境", start_time="05-28 10:30", status="成功", success_rate=98.3),
            ExecutionRecord(exec_id="#20240527015", plan_name="支付接口专项测试", type="API", env="测试环境", start_time="05-27 18:45", status="失败", success_rate=85.7),
            ExecutionRecord(exec_id="#20240527014", plan_name="系统性能测试", type="性能", env="预发环境", start_time="05-27 16:20", status="成功", success_rate=100.0),
            ExecutionRecord(exec_id="#20240527013", plan_name="UI 冒烟测试", type="UI", env="测试环境", start_time="05-27 09:15", status="成功", success_rate=97.1),
            ExecutionRecord(exec_id="#20240526008", plan_name="下单模块回归", type="API / UI", env="测试环境", start_time="05-26 20:10", status="成功", success_rate=96.6),
        ],
    )
