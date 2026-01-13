from __future__ import annotations
import dataclasses, json
from datetime import date, datetime
from typing import Any
import re


def to_jsonable(obj: Any, *, max_str_len: int | None = None) -> Any:
    """
    Summary: 다양한 객체를 JSON 직렬화 가능한 구조로 변환합니다.

    Contract:
        - 길이 제한이 있으면 문자열/바이너리를 잘라냅니다.
        - 지원되지 않는 타입은 repr로 폴백합니다.

    Args:
        obj: 변환 대상 객체.
        max_str_len: 문자열 최대 길이(옵션).

    Returns:
        Any: JSON 직렬화 가능한 값.
    """
    if obj is None or isinstance(obj, (bool, int, float)):
        return obj

    if isinstance(obj, str):
        if max_str_len and len(obj) > max_str_len:
            return obj[:max_str_len] + "…"
        return obj

    if isinstance(obj, (bytes, bytearray, memoryview)):
        try:
            s = bytes(obj).decode("utf-8", "replace")
        except Exception:
            s = repr(obj)
        if max_str_len and len(s) > max_str_len:
            return s[:max_str_len] + "…"
        return s

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, dict):
        return {str(k): to_jsonable(v, max_str_len=max_str_len) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(v, max_str_len=max_str_len) for v in obj]

    if dataclasses.is_dataclass(obj):
        return to_jsonable(dataclasses.asdict(obj), max_str_len=max_str_len)

    try:
        from pydantic import BaseModel

        if isinstance(obj, BaseModel):
            return to_jsonable(obj.model_dump(), max_str_len=max_str_len)
    except Exception:
        pass

    try:
        from langchain_core.messages import BaseMessage

        if isinstance(obj, BaseMessage):
            base = {
                "type": getattr(obj, "type", obj.__class__.__name__),
                "content": to_jsonable(
                    getattr(obj, "content", None), max_str_len=max_str_len
                ),
            }
            for attr in ("name", "id", "tool_call_id", "additional_kwargs"):
                if hasattr(obj, attr):
                    base[attr] = to_jsonable(
                        getattr(obj, attr), max_str_len=max_str_len
                    )
            return base
    except Exception:
        pass

    if isinstance(obj, BaseException):
        return {"error": str(obj), "type": obj.__class__.__name__}

    try:
        json.dumps(obj)
        return obj
    except Exception:
        return repr(obj)


def parse_jsonish(v: Any) -> Any:
    """
    Summary: 문자열 형태의 JSON 또는 유사 로그를 안전하게 파싱합니다.

    Contract:
        - dict/list는 그대로 반환합니다.
        - 문자열은 JSON 파싱 시도 후 실패 시 패턴 기반으로 추출합니다.

    Args:
        v: 입력 값.

    Returns:
        Any: 파싱된 객체 또는 원문/표현 문자열.
    """
    if v is None:
        return None
    if isinstance(v, (dict, list)):
        return v
    if isinstance(v, (bytes, bytearray, memoryview)):
        try:
            v = bytes(v).decode("utf-8", "replace")
        except Exception:
            v = repr(v)
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        # 1) 순수 JSON 시도
        try:
            return json.loads(s)
        except Exception:
            pass
        # 2) LangChain ToolMessage 문자열 로그 패턴: content='...'
        m = re.search(r"content='(.+?)'", s)
        if m:
            inner = m.group(1)
            try:
                return json.loads(inner)
            except Exception:
                return inner
        return s
    # 기타 타입은 repr로 안전하게
    try:
        json.dumps(v)
        return v
    except Exception:
        return repr(v)
