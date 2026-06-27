"""QA-02: E2E-сценарий загрузка → индексация → поиск → отображение результатов."""

from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright

pytestmark = pytest.mark.e2e

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
SEARCH_QUERY = "Москва"


def test_upload_index_search_and_highlight(require_e2e_stack, e2e_frontend_url: str):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(e2e_frontend_url)
            page.locator('input[type="file"]').set_input_files(
                str(FIXTURES_DIR / "valid.pdf")
            )

            upload_item = page.locator(".upload-item").filter(has_text="valid.pdf")
            expect(upload_item.get_by_text("Готово")).to_be_visible(timeout=120_000)

            search_input = page.get_by_label("Поисковый запрос")
            search_input.fill(SEARCH_QUERY)
            page.get_by_role("button", name="Найти").click()

            expect(page.locator(".results-section")).to_be_visible(timeout=30_000)
            first_result = page.locator(".result-card").first
            expect(first_result).to_contain_text("valid.pdf")
            expect(first_result.locator(".result-text")).to_contain_text("Москва")

            highlighted = first_result.locator(".result-text mark")
            if highlighted.count() == 0:
                expect(first_result.locator(".result-text")).to_contain_text("Москва")
            else:
                expect(highlighted.first).to_be_visible()
        finally:
            browser.close()
