import re

import allure
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ProductPage(BasePage):
    PRICE_PATTERN = re.compile(r"\d[\d\s]*\s*₽")
    CART_BUTTON_PATTERN = re.compile(r"корзин", re.IGNORECASE)

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Проверить, что открылась страница товара (URL содержит /product/)")
    def expect_opened(self) -> None:
        expect(self.page).to_have_url(re.compile(r"/product/"), timeout=20_000)

    @allure.step("Проверить наличие названия и цены")
    def expect_title_and_price(self) -> None:
        expect(self.page.locator("h1").first).to_be_visible(timeout=20_000)
        expect(
            self.page.get_by_text(self.PRICE_PATTERN).first
        ).to_be_visible(timeout=20_000)

    @allure.step("Проверить наличие кнопки «В корзину»")
    def expect_add_to_cart_button(self) -> None:
        expect(
            self.page.get_by_role("button", name=self.CART_BUTTON_PATTERN).first
        ).to_be_visible(timeout=20_000)
