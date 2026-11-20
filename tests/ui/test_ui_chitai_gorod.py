import re

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.main_page import MainPage
from pages.product_page import ProductPage


@allure.epic("Читай-город")
@allure.story("UI Тестирование")
class TestChitaiGorodUI:

    @allure.title("Поиск книги по названию")
    @pytest.mark.ui
    def test_search_book_by_title(self, page: Page, base_url: str, search_query: str) -> None:
        main_page = MainPage(page)

        with allure.step(f"Открыть главную страницу {base_url}"):
            main_page.open(base_url)

        with allure.step(f"Найти товар по запросу «{search_query}»"):
            main_page.search(search_query)

        with allure.step("Проверить заголовок «Нашли N товаров»"):
            main_page.expect_results_found()

    @allure.title("Поиск отображает карточки товаров")
    @pytest.mark.ui
    def test_search_displays_product_cards(self, page: Page, base_url: str, search_query: str) -> None:
        main_page = MainPage(page)

        with allure.step("Открыть главную и выполнить поиск"):
            main_page.open(base_url)
            main_page.search(search_query)

        with allure.step("Проверить наличие карточек товаров"):
            main_page.expect_product_cards()

    @allure.title("Переход в карточку товара из выдачи: название, цена, кнопка «В корзину»")
    @pytest.mark.ui
    def test_open_product_card_from_search(self, page: Page, base_url: str, search_query: str) -> None:
        main_page = MainPage(page)
        product_page = ProductPage(page)

        with allure.step("Выполнить поиск и открыть первый товар"):
            main_page.open(base_url)
            main_page.search(search_query)
            main_page.expect_product_cards()
            main_page.open_first_product()

        with allure.step("Проверить страницу товара"):
            product_page.expect_opened()
            product_page.expect_title_and_price()
            product_page.expect_add_to_cart_button()

    @allure.title("Поиск по автору: в выдаче присутствует автор")
    @pytest.mark.ui
    @pytest.mark.parametrize(
        ("query", "expected_text"),
        [("Стивен Кинг", re.compile(r"Кинг", re.IGNORECASE)), ("гарри-поттер", re.compile(r"поттер", re.IGNORECASE))],
    )
    def test_search_by_author(self, page: Page, base_url: str, query: str, expected_text: re.Pattern[str]) -> None:
        main_page = MainPage(page)

        with allure.step(f"Открыть главную и найти «{query}»"):
            main_page.open(base_url)
            main_page.search(query)
            main_page.expect_results_found()

        with allure.step(f"Проверить, что в выдаче есть текст «{expected_text.pattern}»"):
            expect(page.get_by_text(expected_text).first).to_be_visible(timeout=20_000)

    @allure.title("Панель фильтров отображается на странице результатов")
    @pytest.mark.ui
    def test_filter_panel_visible(self, page: Page, base_url: str, search_query: str) -> None:
        main_page = MainPage(page)

        with allure.step("Выполнить поиск"):
            main_page.open(base_url)
            main_page.search(search_query)
            main_page.expect_results_found()

        with allure.step("Проверить кнопки фильтров «Категории/Наличие/Статус/Авторы»"):
            main_page.expect_filter_buttons(MainPage.FILTER_NAMES)

    @allure.title("Клик по логотипу возвращает на главную страницу")
    @pytest.mark.ui
    def test_logo_returns_to_home(self, page: Page, base_url: str, search_query: str) -> None:
        main_page = MainPage(page)

        with allure.step("Выполнить поиск"):
            main_page.open(base_url)
            main_page.search(search_query)
            main_page.expect_results_found()

        with allure.step("Кликнуть по логотипу"):
            main_page.click_logo()

        with allure.step("Проверить возврат на главную"):
            expect(page).to_have_url(re.compile(r"chitai-gorod\.ru/?$"), timeout=20_000)
