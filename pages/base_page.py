import re

import allure
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    @allure.step("Открыть страницу: {url}")
    def open(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(2000)
        self.close_popups()

    @allure.step("Закрыть попап выбора города и cookie-баннер")
    def close_popups(self) -> None:
        # 1. Попап «Ваш город — Москва?» -> «Да, я здесь»
        try:
            self.page.get_by_text(
                re.compile(r"да,?\s*я\s*здесь", re.IGNORECASE)
            ).first.click(timeout=4000)
            self.page.wait_for_timeout(500)
        except PlaywrightTimeoutError:
            pass

        # 2. Cookie-баннер «Понятно, закрыть» / «Разрешить»
        try:
            self.page.get_by_role(
                "button", name=re.compile(r"понятно|разрешить|принять|соглас", re.IGNORECASE)
            ).first.click(timeout=3000)
        except PlaywrightTimeoutError:
            pass

        # 3. Универсальное закрытие модалок
        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass