# app/utils/mcp.py
from __future__ import annotations
from typing import Any, Iterable

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


ALLOWED_TRANSPORTS = {"streamable_http", "sse"}


def _normalize_server_config(item: Any) -> tuple[str, dict[str, Any]]:
    """
    입력: MCPServer 모델 인스턴스 or {"name":..., "config":{...}} dict
    출력: (name, config) 튜플 (config에는 최소한 transport/url이 포함)
    """
    if hasattr(item, "name") and hasattr(item, "config"):
        name = item.name
        cfg = dict(item.config or {})
    elif isinstance(item, dict) and "name" in item and "config" in item:
        name = item["name"]
        cfg = dict(item["config"] or {})
    else:
        raise ValueError(
            "MCP 서버 정의는 MCPServer 인스턴스 또는 {'name','config'} dict 여야 합니다."
        )

    transport = cfg.get("transport")
    url = cfg.get("url")
    if transport not in ALLOWED_TRANSPORTS:
        raise ValueError(
            f"허용되지 않는 transport: {transport!r}. 허용: {sorted(ALLOWED_TRANSPORTS)}"
        )
    if not url:
        raise ValueError("MCP config.url 이 필요합니다.")

    headers = cfg.get("headers")
    normalized = {
        "transport": transport,
        "url": url,
        **({"headers": headers} if headers else {}),
    }
    return name, normalized


async def load_mcp_tools_from_servers(servers: Iterable[Any]) -> list[BaseTool]:
    """
    servers: MCPServer 인스턴스들 또는 {"name": str, "config": {...}} dict 들
    반환: LangChain BaseTool 리스트
    """
    server_map: dict[str, dict[str, Any]] = {}
    for item in servers:
        name, cfg = _normalize_server_config(item)
        server_map[name] = cfg

    client = MultiServerMCPClient(server_map)
    tools = await client.get_tools()
    return tools
