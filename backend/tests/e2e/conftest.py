import pytest

from tests.helpers.stack import FRONTEND_URL, is_stack_available


@pytest.fixture(scope="session")
def require_e2e_stack():
    if not is_stack_available(require_frontend=True):
        pytest.skip(
            "E2E: запустите Elasticsearch, Redis, backend и frontend "
            f"(API + {FRONTEND_URL})"
        )

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            browser.close()
    except Exception as exc:
        pytest.skip(f"E2E: выполните `playwright install chromium` ({exc})")


@pytest.fixture(scope="session")
def e2e_frontend_url() -> str:
    return FRONTEND_URL
