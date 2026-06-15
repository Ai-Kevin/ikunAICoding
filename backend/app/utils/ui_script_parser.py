import re


MAX_UI_SCRIPT_SIZE = 10 * 1024 * 1024
VALID_FILENAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_\-\.]*\.py$")


def validate_py_filename(filename: str) -> None:
    if not filename.lower().endswith(".py"):
        raise ValueError("仅支持上传 .py 文件")
    if re.search(r"[\u4e00-\u9fff]", filename):
        raise ValueError("文件名不能包含中文")
    if " " in filename:
        raise ValueError("文件名不能包含空格")
    if not VALID_FILENAME.match(filename):
        raise ValueError("文件名仅允许字母、数字、下划线、连字符和点")


def _humanize_name(filename: str) -> str:
    stem = filename.rsplit(".", 1)[0]
    if stem.startswith("test_"):
        stem = stem[5:]
    parts = [p for p in stem.replace("-", "_").split("_") if p]
    mapping = {
        "login": "登录功能测试",
        "cart": "购物车测试",
        "checkout": "结算流程测试",
        "pay": "支付功能测试",
        "order": "下单功能测试",
        "product": "商品功能测试",
    }
    if len(parts) == 1 and parts[0] in mapping:
        return mapping[parts[0]]
    return " ".join(parts) if parts else stem


def _extract_quoted(text: str) -> str:
    for pattern in (r"'([^']*)'", r'"([^"]*)"'):
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return ""


def parse_ui_script(content: str, filename: str) -> dict:
    lines = content.splitlines()
    module = "默认模块"
    tags = "P2"
    browser = "Chrome"
    priority = "中"
    name = _humanize_name(filename)

    for line in lines[:30]:
        stripped = line.strip()
        lower = stripped.lower()
        if stripped.startswith("# module:"):
            module = stripped.split(":", 1)[1].strip() or module
        elif stripped.startswith("# name:"):
            name = stripped.split(":", 1)[1].strip() or name
        elif stripped.startswith("# tags:"):
            tags = stripped.split(":", 1)[1].strip() or tags
        elif "module" in lower and "登录" in stripped:
            module = "登录模块"
        elif "module" in lower and "购物车" in stripped:
            module = "购物车模块"

    steps: list[dict] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if stripped.startswith("# step:"):
                desc = stripped.split(":", 1)[1].strip()
                steps.append(
                    {"action": "断言", "locator": "", "value": "", "desc": desc}
                )
            continue

        if "driver.get(" in stripped or "webdriver.get(" in stripped:
            url = _extract_quoted(stripped)
            steps.append(
                {
                    "action": "打开页面",
                    "locator": url or stripped,
                    "value": "",
                    "desc": "打开目标页面",
                }
            )
        elif ".send_keys(" in stripped:
            locator = _extract_quoted(stripped) or stripped
            value = ""
            if "," in stripped:
                value = _extract_quoted(stripped.split(",", 1)[1]) or ""
            steps.append(
                {
                    "action": "输入",
                    "locator": locator,
                    "value": value,
                    "desc": "输入测试数据",
                }
            )
        elif ".click(" in stripped:
            locator = _extract_quoted(stripped) or stripped
            steps.append(
                {
                    "action": "点击",
                    "locator": locator,
                    "value": "",
                    "desc": "点击页面元素",
                }
            )
        elif "assert" in stripped.lower():
            steps.append(
                {
                    "action": "断言",
                    "locator": "",
                    "value": "",
                    "desc": stripped,
                }
            )
        elif "time.sleep(" in stripped or "WebDriverWait" in stripped:
            steps.append(
                {
                    "action": "等待",
                    "locator": "",
                    "value": _extract_quoted(stripped) or "1s",
                    "desc": "等待页面响应",
                }
            )

    if not steps:
        steps = [
            {
                "action": "脚本执行",
                "locator": filename,
                "value": "",
                "desc": "执行 Python 自动化测试脚本",
            }
        ]

    if "smoke" in tags.lower() or "login" in filename.lower():
        priority = "高"
        if "P0" not in tags:
            tags = f"smoke,{tags}" if tags else "smoke,P0"

    preview_lines = lines[:18]
    if len(lines) > 18:
        preview_lines.append("...")

    return {
        "filename": filename,
        "name": name,
        "module": module,
        "tags": tags,
        "browser": browser,
        "priority": priority,
        "line_count": len(lines),
        "file_size": len(content.encode("utf-8")),
        "steps": steps,
        "script_preview": "\n".join(preview_lines),
    }
