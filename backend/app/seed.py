import json
from datetime import datetime, timedelta

from sqlalchemy import inspect, text

from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models.models import (
    ApiCase,
    Module,
    Project,
    ProjectMember,
    UiCase,
    UiExecutionRecord,
    User,
)


def migrate_ui_case_columns() -> None:
    inspector = inspect(engine)
    if "ui_cases" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("ui_cases")}
    statements = []
    if "tags" not in columns:
        statements.append("ALTER TABLE ui_cases ADD COLUMN tags VARCHAR(255) DEFAULT ''")
    if "filename" not in columns:
        statements.append("ALTER TABLE ui_cases ADD COLUMN filename VARCHAR(128) DEFAULT ''")
    if "is_enabled" not in columns:
        statements.append("ALTER TABLE ui_cases ADD COLUMN is_enabled INTEGER DEFAULT 1")
    if "created_at" not in columns:
        statements.append("ALTER TABLE ui_cases ADD COLUMN created_at DATETIME")
    if not statements:
        return
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
    columns = {col["name"] for col in inspect(engine).get_columns("ui_cases")}
    if "created_at" in columns:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE ui_cases SET created_at = updated_at "
                    "WHERE created_at IS NULL"
                )
            )


def seed_ui_executions() -> None:
    db = SessionLocal()
    try:
        if db.query(UiExecutionRecord).first():
            return

        demo_rows = [
            ("20240615103225001", "登录功能测试", "测试环境", 1, 1, 0, 0, 100.0, 35, "Docker 执行机-01", "admin", "成功", datetime(2024, 6, 15, 10, 32, 25)),
            ("20240615104532002", "购物车结算流程", "测试环境", 3, 3, 0, 0, 100.0, 72, "Docker 执行机-01", "admin", "成功", datetime(2024, 6, 15, 10, 45, 32)),
            ("20240615112015003", "支付密码校验", "测试环境", 2, 1, 1, 0, 50.0, 48, "Docker 执行机-01", "test01", "失败", datetime(2024, 6, 15, 11, 20, 15)),
            ("20240614153022004", "验证码登录测试", "预发环境", 1, 1, 0, 0, 100.0, 28, "本地执行", "admin", "成功", datetime(2024, 6, 14, 15, 30, 22)),
            ("20240614181543005", "用户中心信息修改", "测试环境", 4, 2, 2, 0, 50.0, 95, "Docker 执行机-02", "李四", "失败", datetime(2024, 6, 14, 18, 15, 43)),
            ("20240614102008006", "商品详情页展示", "测试环境", 2, 2, 0, 0, 100.0, 41, "Docker 执行机-01", "王五", "成功", datetime(2024, 6, 14, 10, 20, 8)),
            ("20240613164512007", "下单收货地址校验", "测试环境", 5, 4, 1, 0, 80.0, 118, "Docker 执行机-01", "赵六", "失败", datetime(2024, 6, 13, 16, 45, 12)),
            ("20240613113055008", "登录功能测试", "测试环境", 1, 1, 0, 0, 100.0, 33, "Docker 执行机-02", "admin", "成功", datetime(2024, 6, 13, 11, 30, 55)),
            ("20240612142030009", "购物车添加商品测试", "预发环境", 2, 2, 0, 0, 100.0, 56, "本地执行", "test01", "成功", datetime(2024, 6, 12, 14, 20, 30)),
            ("20240612101518010", "支付密码校验", "测试环境", 3, 2, 1, 0, 66.7, 89, "Docker 执行机-01", "张三", "失败", datetime(2024, 6, 12, 10, 15, 18)),
            ("20240611163042011", "批量执行-5个用例", "测试环境", 5, 5, 0, 0, 100.0, 138, "Docker 执行机-01", "admin", "成功", datetime(2024, 6, 11, 16, 30, 42)),
            ("20240611104508012", "记住登录测试", "测试环境", 1, 0, 1, 0, 0.0, 22, "Docker 执行机-02", "李四", "失败", datetime(2024, 6, 11, 10, 45, 8)),
            ("20240610152033013", "验证码登录测试", "测试环境", 2, 2, 0, 0, 100.0, 44, "Docker 执行机-01", "王五", "成功", datetime(2024, 6, 10, 15, 20, 33)),
            ("20240610103527014", "登录功能测试", "生产环境", 1, 1, 0, 0, 100.0, 31, "本地执行", "admin", "成功", datetime(2024, 6, 10, 10, 35, 27)),
            ("20240609141852015", "购物车结算流程", "测试环境", 4, 3, 1, 0, 75.0, 102, "Docker 执行机-01", "test01", "失败", datetime(2024, 6, 9, 14, 18, 52)),
            ("20240609103015016", "用户中心信息修改", "测试环境", 2, 2, 0, 0, 100.0, 52, "Docker 执行机-02", "赵六", "成功", datetime(2024, 6, 9, 10, 30, 15)),
            ("20240608162548017", "商品详情页展示", "预发环境", 1, 1, 0, 0, 100.0, 26, "Docker 执行机-01", "张三", "成功", datetime(2024, 6, 8, 16, 25, 48)),
            ("20240608111022018", "支付密码校验", "测试环境", 3, 3, 0, 0, 100.0, 67, "Docker 执行机-01", "admin", "成功", datetime(2024, 6, 8, 11, 10, 22)),
            ("20240607153008019", "下单收货地址校验", "测试环境", 2, 1, 1, 0, 50.0, 58, "本地执行", "李四", "失败", datetime(2024, 6, 7, 15, 30, 8)),
            ("20240607104533020", "登录功能测试", "测试环境", 1, 1, 0, 0, 100.0, 34, "Docker 执行机-01", "王五", "成功", datetime(2024, 6, 7, 10, 45, 33)),
        ]

        for row in demo_rows:
            task_id, name, env, total, succ, fail, skip, rate, dur, machine, creator, status, start = row
            end = start + timedelta(seconds=dur)
            db.add(
                UiExecutionRecord(
                    task_id=task_id,
                    name=name,
                    env=env,
                    total_cases=total,
                    success_count=succ,
                    fail_count=fail,
                    skip_count=skip,
                    success_rate=rate,
                    duration_seconds=dur,
                    machine=machine,
                    mode="parallel",
                    creator=creator,
                    status=status,
                    logs=f"[INFO] 任务 {task_id} 执行完成\n[INFO] 成功 {succ} · 失败 {fail}",
                    start_time=start,
                    end_time=end,
                )
            )

        db.commit()
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    migrate_ui_case_columns()
    seed_ui_executions()
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
            UiCase(name="登录功能测试", module="登录模块", browser="Chrome", priority="高", status="已通过", tags="smoke,P0", filename="test_login.py", is_enabled=1, step_count=len(login_steps), creator="admin", steps=steps_json(login_steps)),
            UiCase(name="验证码登录测试", module="登录模块", browser="Chrome", priority="中", status="已通过", tags="regression,P1", filename="test_login_sms.py", is_enabled=1, step_count=6, creator="admin", steps=steps_json(login_steps[:6])),
            UiCase(name="记住登录测试", module="登录模块", browser="Chrome", priority="低", status="未执行", tags="P2", filename="test_remember_login.py", is_enabled=0, step_count=5, creator="admin", steps=steps_json(login_steps[:5])),
            UiCase(name="购物车添加商品测试", module="购物车模块", browser="Chrome", priority="高", status="已通过", tags="smoke,P0", filename="test_cart_add.py", is_enabled=1, step_count=7, creator="test01", steps=steps_json(login_steps)),
            UiCase(name="购物车结算流程", module="购物车模块", browser="Chrome", priority="高", status="已通过", tags="regression,P0", filename="test_cart_checkout.py", is_enabled=1, step_count=7, creator="李四", steps=steps_json(login_steps)),
            UiCase(name="下单收货地址校验", module="下单模块", browser="Firefox", priority="中", status="失败", tags="regression,P1", filename="test_order_address.py", is_enabled=1, step_count=7, creator="王五", steps=steps_json(login_steps)),
            UiCase(name="支付密码校验", module="支付模块", browser="Chrome", priority="高", status="已通过", tags="smoke,P0", filename="test_pay_password.py", is_enabled=1, step_count=7, creator="赵六", steps=steps_json(login_steps)),
            UiCase(name="用户中心信息修改", module="用户中心", browser="Edge", priority="中", status="已通过", tags="P1", filename="test_profile_edit.py", is_enabled=1, step_count=7, creator="张三", steps=steps_json(login_steps)),
            UiCase(name="商品详情页展示", module="商品模块", browser="Chrome", priority="中", status="已通过", tags="regression,P2", filename="test_product_detail.py", is_enabled=1, step_count=6, creator="李四", steps=steps_json(login_steps[:6])),
        ]
        db.add_all(ui_cases)

        db.commit()
    finally:
        db.close()
