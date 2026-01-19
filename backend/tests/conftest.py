import sys
import asyncio

import pytest_asyncio
from pathlib import Path

# 테스트에서 앱 임포트가 되도록 백엔드 루트를 sys.path에 추가한다.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest_asyncio.fixture(scope="session")
def event_loop():
    # 전체 테스트 세션용 전용 이벤트 루프를 제공해
    # 다른 곳에서 만든 전역 루프를 공유하지 않도록 한다.
    loop = asyncio.new_event_loop()
    yield loop
    # 경고와 리소스 누수를 막기 위해 루프를 항상 닫는다.
    loop.close()
