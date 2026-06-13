import re

from fastapi import Request


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _extract_version(ua: str, marker: str) -> str:
    idx = ua.find(marker)
    if idx == -1:
        return ""
    tail = ua[idx + len(marker) :]
    match = re.match(r"([\d.]+)", tail)
    return match.group(1) if match else ""


def parse_user_agent(user_agent: str) -> tuple[str, str]:
    ua = user_agent or ""
    ua_lower = ua.lower()

    if any(k in ua_lower for k in ("iphone", "ipad", "android", "mobile")):
        device = "mobile"
    else:
        device = "desktop"

    if "windows" in ua_lower:
        os_name = "Windows"
    elif "mac os x" in ua_lower or "macintosh" in ua_lower:
        os_name = "macOS"
    elif "iphone" in ua_lower or "ipad" in ua_lower:
        os_name = "iOS"
    elif "android" in ua_lower:
        os_name = "Android"
    elif "linux" in ua_lower:
        os_name = "Linux"
    else:
        os_name = "未知系统"

    if "edg/" in ua_lower:
        browser = f"Edge {_extract_version(ua, 'Edg/')}".strip()
    elif "chrome/" in ua_lower:
        browser = f"Chrome {_extract_version(ua, 'Chrome/')}".strip()
    elif "firefox/" in ua_lower:
        browser = f"Firefox {_extract_version(ua, 'Firefox/')}".strip()
    elif "safari/" in ua_lower:
        browser = f"Safari {_extract_version(ua, 'Version/')}".strip()
    else:
        browser = "未知浏览器"

    return device, f"{os_name} 登录 · {browser}"


def format_location(ip: str) -> str:
    if ip in ("127.0.0.1", "::1", "localhost", "unknown"):
        return "本地网络"
    if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
        return "内网"
    return f"IP {ip}"
