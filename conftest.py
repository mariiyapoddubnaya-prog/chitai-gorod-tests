import os
from typing import Iterator
import re
import pytest
import requests
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

load_dotenv()


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "https://www.chitai-gorod.ru")


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return os.getenv("API_BASE_URL", "https://www.chitai-gorod.ru")


@pytest.fixture(scope="session")
def search_query() -> str:
    return os.getenv("SEARCH_QUERY", "гарри-поттер")


@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    channel = os.getenv("BROWSER_CHANNEL", "").strip() or None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, channel=channel)
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def browser_context(browser: Browser) -> Iterator[BrowserContext]:
    context = browser.new_context(locale="ru-RU", viewport={"width": 1600, "height": 900})
    context.set_default_timeout(60_000)
    yield context
    context.close()


@pytest.fixture
def page(browser_context: BrowserContext) -> Iterator[Page]:
    new_page = browser_context.new_page()
    new_page.set_default_timeout(60_000)
    yield new_page
    new_page.close()


@pytest.fixture(scope="session")
def api_session(base_url: str) -> Iterator[requests.Session]:
    """Сессия с браузерными заголовками: без них сайт отдаёт 404/антибот."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            "Referer": f"{base_url}/",
        }
    )
    yield session
    session.close()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Автоматически делает скриншот при падении UI-теста"""
    outcome = yield
    rep = outcome.get_result()

    # Если тест упал на этапе выполнения (call) и это UI тест
    if rep.when == "call" and rep.failed and "page" in item.fixturenames:
        page = item.funcargs["page"]
        # Очищаем имя теста для названия файла
        test_name = item.name.replace("[", "_").replace("]", "_").replace(" ", "_")
        screenshot_path = f"failure_{test_name}.png"

        try:
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"\n[DEBUG] Скриншот ошибки сохранен: {screenshot_path}")
        except Exception as e:
            print(f"\n[DEBUG] Не удалось сделать скриншот: {e}")


@pytest.fixture(scope="session")
def product_path(api_session: requests.Session, base_url: str) -> str:
    """Получает реальный путь карточки товара из HTML главной страницы."""
    response = api_session.get(base_url, timeout=20)
    assert response.status_code == 200
    match = re.search(
        r'href="(?:https?://www\.chitai-gorod\.ru)?(/product/[^"?#]+)"',
        response.text,
    )
    assert match, "На главной странице не найдена ссылка на товар (/product/...)"
    return match.group(1)