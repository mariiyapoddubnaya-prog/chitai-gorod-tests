import re

import allure
from playwright.sync_api import Locator, Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage


class MainPage(BasePage):
    PRODUCT_LINK = "a[href*='/product/']"
    FILTER_NAMES = ("Категории", "Наличие", "Статус", "Авторы")

    # Кликабельные элементы подсказок (не обёртки!)
    SUGGESTION_SELECTORS = (
        "[class*='uggest'] a",
        "[class*='uggest'] li",
        "[role='listbox'] li",
        "[role='option']",
    )

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Найти поле поиска в шапке")
    def _find_search_input(self) -> Locator:
        search_input = self.page.get_by_placeholder(
            re.compile(r"поиск|книг|isbn|автор|товар", re.IGNORECASE)
        ).first
        if search_input.count() == 0:
            search_input = self.page.locator("header").get_by_role("textbox").first
        if search_input.count() == 0:
            search_input = self.page.locator("header input").first
        return search_input

    @allure.step("Дождаться появления подсказок по слову «{first_word}»")
    def _wait_suggestions(self, first_word: str) -> None:
        pattern = re.compile(re.escape(first_word), re.IGNORECASE)
        try:
            self.page.get_by_text(pattern).last.wait_for(state="visible", timeout=8_000)
        except PlaywrightTimeoutError:
            pass

    @allure.step("Дождаться перехода на страницу результатов")
    def _wait_for_search_page(self, timeout: int = 15_000) -> None:
        # expect.to_have_url поллит page.url и НЕ требует события 'load' —
        # это единственный надёжный способ для SPA (Nuxt) с клиентской навигацией
        expect(self.page).to_have_url(re.compile(r"/search"), timeout=timeout)

    @allure.step("Поиск с клавиатуры: стрелка вниз + Enter (с ретраями)")
    def _keyboard_search(self, query: str, attempts: int = 3) -> bool:
        search_input = self._find_search_input()
        first_word = query.split("-")[0].split()[0]
        for _ in range(attempts):
            search_input.press("ArrowDown")
            search_input.press("Enter")
            try:
                self._wait_for_search_page(timeout=8_000)
                return True
            except (PlaywrightTimeoutError, AssertionError):
                # Потеря фокуса/dropdown закрылся — перефокус и повторный ввод
                try:
                    search_input.click(force=True)
                    search_input.fill(query)
                    self._wait_suggestions(first_word)
                except Exception:
                    pass
        return False

    @allure.step("Клик по первой подсказке из dropdown")
    def _click_suggestion(self, query: str) -> bool:
        first_word = query.split("-")[0].split()[0]
        pattern = re.compile(re.escape(first_word), re.IGNORECASE)
        for selector in self.SUGGESTION_SELECTORS:
            try:
                item = self.page.locator(selector).filter(has_text=pattern).last
                item.wait_for(state="visible", timeout=2_000)
                item.click()
                return True
            except Exception:
                continue
        return False

    @allure.step("Ввести запрос «{query}» и открыть страницу результатов")
    def search(self, query: str) -> None:
        self.close_popups()

        search_input = self._find_search_input()
        search_input.scroll_into_view_if_needed()
        search_input.click(force=True)
        search_input.fill(query)

        first_word = query.split("-")[0].split()[0]
        self._wait_suggestions(first_word)

        # Путь 1 (проверенный этим прогоном): клавиатура
        if self._keyboard_search(query):
            return

        # Путь 2: клик по подсказке (обёрнут, чтобы не ронять тест)
        if self._click_suggestion(query):
            try:
                self._wait_for_search_page(timeout=10_000)
                return
            except AssertionError:
                pass

        # Путь 3: кнопка-лупа в шапке
        try:
            self.page.locator("header button").last.click(force=True)
        except Exception:
            pass
        self._wait_for_search_page(timeout=15_000)

    @allure.step("Проверить наличие результатов поиска (карточек товаров)")
    def expect_results_found(self) -> None:
        expect(self.page.locator(self.PRODUCT_LINK).first).to_be_visible(timeout=20_000)

    @allure.step("Проверить наличие карточек товаров")
    def expect_product_cards(self) -> None:
        self.expect_results_found()

    @allure.step("Открыть первую карточку товара")
    def open_first_product(self) -> None:
        self.page.locator(self.PRODUCT_LINK).first.click()

    @allure.step("Проверить панель фильтров: {names}")
    def expect_filter_buttons(self, names: tuple[str, ...]) -> None:
        for name in names:
            expect(self.page.get_by_text(re.compile(name)).first).to_be_visible(timeout=10_000)

    @allure.step("Кликнуть по логотипу для возврата на главную")
    def click_logo(self) -> None:
        logo = self.page.locator("header a[href='/']").first
        if logo.count() == 0:
            logo = self.page.locator("header a").first
        logo.click(force=True)
