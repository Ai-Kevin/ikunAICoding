import json
from datetime import datetime

from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models.models import (
    ApiCase,
    Module,
    Project,
    ProjectMember,
    UiCase,
    User,
)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).first():
            return  # already seeded

        # ----- default admin user -----
        db.add(
            User(
                username="admin",
                email="admin@autotest.com",
                hashed_password=get_password_hash("admin123"),
                role="ADMIN",
            )
        )

        # ----- demo project -----
        project = Project(
            name="电商平台项目",
            code="PRJ_20240315001",
            status="进行中",
            owner="Admin",
            dept="质量保障部",
            project_type="Web + App + 后台",
            version="V2.3.0",
            git_repo="https://git.example.com/qa/ecommerce.git",
            description="电商平台系统的自动化测试项目，包含 Web、App、管理后台等多个系统的测试。",
            created_at=datetime(2024, 3, 15),
        )
        modules = [
            Module(name="用户模块", type="业务模块", api_count=312, ui_count=68, perf_count=12, pass_rate=98.2, owner="张三"),
            Module(name="商品模块", type="业务模块", api_count=428, ui_count=92, perf_count=18, pass_rate=97.1, owner="李四"),
            Module(name="订单模块", type="业务模块", api_count=286, ui_count=54, perf_count=10, pass_rate=95.3, owner="王五"),
            Module(name="支付模块", type="业务模块", api_count=158, ui_count=32, perf_count=8, pass_rate=96.7, owner="赵六"),
            Module(name="促销模块", type="业务模块", api_count=100, ui_count=18, perf_count=6, pass_rate=93.8, owner="孙七"),
            Module(name="后台管理", type="系统模块", api_count=210, ui_count=62, perf_count=15, pass_rate=98.9, owner="周八"),
            Module(name="App 客户端", type="客户端", api_count=120, ui_count=0, perf_count=8, pass_rate=97.2, owner="吴九"),
        ]
        project.modules = modules
        project.members = [
            ProjectMember(name="Admin", role="项目负责人", email="admin@autotest.com"),
            ProjectMember(name="张三", role="测试负责人", email="zhangsan@autotest.com"),
            ProjectMember(name="李四", role="测试工程师", email="lisi@autotest.com"),
            ProjectMember(name="王五", role="测试工程师", email="wangwu@autotest.com"),
            ProjectMember(name="赵六", role="开发对接人", email="zhaoliu@autotest.com"),
        ]
        db.add(project)

        # ----- API cases -----
        default_headers = json.dumps(
            {"Content-Type": "application/json"}, ensure_ascii=False, indent=2
        )
        create_user_body = json.dumps(
            {
                "username": "test_admin",
                "password": "123456",
                "email": "test@example.com",
                "mobile": "13800138000",
                "role": "ADMIN",
                "status": 1,
            },
            ensure_ascii=False,
            indent=2,
        )
        create_user_asserts = json.dumps(
            [
                {"enabled": True, "type": "状态码断言", "field": "Status code", "expect": "200"},
                {"enabled": True, "type": "响应时间断言", "field": "Response time(ms)", "expect": "< 500"},
                {"enabled": True, "type": "JSON 字段断言", "field": "$.code", "expect": "200"},
                {"enabled": True, "type": "JSON 字段断言", "field": "$.message", "expect": "创建用户成功"},
                {"enabled": True, "type": "JSON 字段断言", "field": "$.data.userId", "expect": "符合正则: ^\\d+$"},
            ],
            ensure_ascii=False,
        )
        status_assert = json.dumps(
            [{"enabled": True, "type": "状态码断言", "field": "Status code", "expect": "200"}],
            ensure_ascii=False,
        )
        api_cases = [
            ApiCase(name="获取用户列表", method="GET", url="{{baseUrl}}/api/v1/users", module="用户模块", priority="高", status="已启用", tags="高优先级,核心用例", headers=default_headers, assertions=status_assert),
            ApiCase(name="创建用户", method="POST", url="{{baseUrl}}/api/v1/users/create", module="用户模块", priority="高", status="已启用", tags="高优先级,核心用例", headers=default_headers, body=create_user_body, assertions=create_user_asserts),
            ApiCase(name="更新用户信息", method="PUT", url="{{baseUrl}}/api/v1/users/update", module="用户模块", priority="中", status="已启用", tags="回归测试", headers=default_headers, assertions=status_assert),
            ApiCase(name="删除用户", method="DELETE", url="{{baseUrl}}/api/v1/users/delete", module="用户模块", priority="中", status="已启用", tags="回归测试", headers=default_headers, assertions=status_assert),
            ApiCase(name="商品搜索", method="GET", url="{{baseUrl}}/api/v1/products/search", module="商品模块", priority="高", status="已启用", tags="核心用例", headers=default_headers, assertions=status_assert),
            ApiCase(name="提交订单", method="POST", url="{{baseUrl}}/api/v1/orders/submit", module="订单模块", priority="高", status="已启用", tags="高优先级,冒烟测试", headers=default_headers, assertions=status_assert),
            ApiCase(name="支付下单", method="POST", url="{{baseUrl}}/api/v1/pay/create", module="支付模块", priority="高", status="已启用", tags="高优先级", headers=default_headers, assertions=status_assert),
            ApiCase(name="查询优惠券", method="GET", url="{{baseUrl}}/api/v1/coupons", module="促销模块", priority="低", status="已禁用", tags="回归测试", headers=default_headers, assertions=status_assert),
        ]
        db.add_all(api_cases)

        # ----- UI cases -----
        login_steps = [
            {"action": "打开页面", "locator": "https://test.ecommerce.com/login", "value": "", "desc": "页面标题包含\"用户登录\""},
            {"action": "输入", "locator": "id=username", "value": "test_admin", "desc": "输入框赋值"},
            {"action": "输入", "locator": "id=password", "value": "123456", "desc": "输入框赋值"},
            {"action": "点击", "locator": "id=loginBtn", "value": "", "desc": "无"},
            {"action": "等待", "locator": "id=homePage", "value": "10s", "desc": "首页元素可见"},
            {"action": "断言", "locator": "id=userName", "value": "test_admin", "desc": "文本等于 test_admin"},
            {"action": "截图", "locator": "全屏截图", "value": "", "desc": "登录成功截图"},
        ]

        def steps_json(steps):
            return json.dumps(steps, ensure_ascii=False)

        ui_cases = [
            UiCase(name="登录功能测试", module="登录模块", browser="Chrome", priority="高", status="已通过", step_count=len(login_steps), creator="Admin", steps=steps_json(login_steps)),
            UiCase(name="验证码登录测试", module="登录模块", browser="Chrome", priority="中", status="已通过", step_count=6, creator="Admin", steps=steps_json(login_steps[:6])),
            UiCase(name="记住登录测试", module="登录模块", browser="Chrome", priority="低", status="未执行", step_count=5, creator="Admin", steps=steps_json(login_steps[:5])),
            UiCase(name="购物车结算流程", module="购物车模块", browser="Chrome", priority="高", status="已通过", step_count=7, creator="李四", steps=steps_json(login_steps)),
            UiCase(name="下单收货地址校验", module="下单模块", browser="Firefox", priority="中", status="失败", step_count=7, creator="王五", steps=steps_json(login_steps)),
            UiCase(name="支付密码校验", module="支付模块", browser="Chrome", priority="高", status="已通过", step_count=7, creator="赵六", steps=steps_json(login_steps)),
            UiCase(name="用户中心信息修改", module="用户中心", browser="Edge", priority="中", status="已通过", step_count=7, creator="张三", steps=steps_json(login_steps)),
            UiCase(name="商品详情页展示", module="商品模块", browser="Chrome", priority="中", status="已通过", step_count=6, creator="李四", steps=steps_json(login_steps[:6])),
        ]
        db.add_all(ui_cases)

        db.commit()
    finally:
        db.close()
