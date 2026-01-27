import sys
import asyncio
import platform

import pytest_asyncio
import pytest
from pathlib import Path
import os

# 테스트에서 앱 임포트가 되도록 백엔드 루트를 sys.path에 추가한다.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Work around WMI hang during SQLAlchemy import on Windows.
platform.machine = lambda: "x86_64"



@pytest_asyncio.fixture(scope="session")
def event_loop():
    # 전체 테스트 세션용 전용 이벤트 루프를 제공해
    # 다른 곳에서 만든 전역 루프를 공유하지 않도록 한다.
    loop = asyncio.new_event_loop()
    yield loop
    # 경고와 리소스 누수를 막기 위해 루프를 항상 닫는다.
    loop.close()


def pytest_collection_modifyitems(config, items):
    # 통합 테스트는 기본 스킵하고 RUN_INTEGRATION=1일 때만 실행.
    run_integration = os.getenv("RUN_INTEGRATION", "").lower() in ("1", "true", "yes")
    skip_integration = pytest.mark.skip(
        reason="integration tests require DB; set RUN_INTEGRATION=1"
    )
    for item in items:
        path = str(item.fspath).replace("\\", "/")
        if "/tests/integration/" in path:
            item.add_marker("integration")
            if not run_integration:
                item.add_marker(skip_integration)


def pytest_configure(config):
    # 로컬 환경에서는 coverage fail-under를 비활성화한다.
    if not os.getenv("CI"):
        config.option.cov_fail_under = 0
