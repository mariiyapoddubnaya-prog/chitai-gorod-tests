import re
from typing import Any

import allure
import pytest
import requests


@allure.epic("Читай-город")
@allure.story("API Тестирование")
class TestChitaiGorodAPI:

    @allure.title("Позитивный: главная страница доступна и возвращает 200")
    @pytest.mark.api
    def test_main_page_available(self, api_session: requests.Session, api_base_url: str) -> None:
        with allure.step(f"GET {api_base_url}"):
            response = api_session.get(api_base_url, timeout=20)

        with allure.step("Проверить статус 200"):
            assert response.status_code == 200, f"Получен {response.status_code}"

        with allure.step("Проверить наличие названия сайта в ответе"):
            assert "Читай-город" in response.text, "Название сайта не найдено в ответе"

    @allure.title("Позитивный: страница поиска доступна и возвращает 200")
    @pytest.mark.api
    def test_search_page_available(self, api_session: requests.Session, api_base_url: str, search_query: str) -> None:
        with allure.step(f"GET {api_base_url}/search?q={search_query}"):
            response = api_session.get(f"{api_base_url}/search", params={"q": search_query}, timeout=20)

        with allure.step("Проверить статус 200"):
            assert response.status_code == 200, f"Получен {response.status_code}"

        with allure.step("Проверить наличие ключевых слов в ответе"):
            body = response.text.lower()
            assert "поиск" in body or "товар" in body or "нашли" in body, (
                "Страница поиска не содержит ожидаемых ключевых слов"
            )

    @allure.title("Позитивный: страница товара доступна (slug из главной)")
    @pytest.mark.api
    def test_product_page_available(self, api_session: requests.Session, api_base_url: str, product_path: str) -> None:
        with allure.step(f"GET {api_base_url}{product_path}"):
            response = api_session.get(f"{api_base_url}{product_path}", timeout=20)

        with allure.step("Проверить статус 200"):
            assert response.status_code == 200, f"Получен {response.status_code}"

        with allure.step("Проверить признаки карточки товара"):
            body = response.text.lower()
            assert "корзин" in body or "руб" in body or "₽" in response.text, (
                "На странице товара не найдены признаки карточки (цена/кнопка «В корзину»)"
            )

    @allure.title("Позитивный: internal-ресурс robots.txt доступен")
    @pytest.mark.api
    def test_static_resource_available(self, api_session: requests.Session, api_base_url: str) -> None:
        with allure.step("GET /robots.txt"):
            response = api_session.get(f"{api_base_url}/robots.txt", timeout=20)

        with allure.step("Проверить статус 200 или 404"):
            assert response.status_code in (200, 404), f"Получен неожиданный статус {response.status_code}"

        if response.status_code == 200:
            with allure.step("Проверить наличие директив robots.txt"):
                body = response.text.lower()
                assert "user-agent" in body or "disallow" in body or "sitemap" in body, (
                    "В robots.txt не найдены ожидаемые директивы"
                )

    @allure.title("Негативный: несуществующая страница возвращает 404")
    @pytest.mark.api
    def test_page_not_found(self, api_session: requests.Session, api_base_url: str) -> None:
        fake_url = f"{api_base_url}/this-page-does-not-exist-12345xyz"
        with allure.step(f"GET {fake_url}"):
            response = api_session.get(fake_url, timeout=20)

        with allure.step("Проверить статус 404"):
            assert response.status_code == 404, f"Получен {response.status_code}"

        with allure.step("Проверить признаки страницы ошибки"):
            body = response.text.lower()
            assert "404" in body or "не найдена" in body or "затерялась" in body, (
                "Страница не содержит признаков ошибки 404"
            )

    @allure.title("Негативный/граничный: пустой поисковый запрос обработан корректно")
    @pytest.mark.api
    def test_search_empty_query(self, api_session: requests.Session, api_base_url: str) -> None:
        with allure.step("GET /search?q="):
            response = api_session.get(f"{api_base_url}/search", params={"q": ""}, timeout=20)

        with allure.step("Проверить статус 200 (сайт не падает)"):
            assert response.status_code == 200, f"Получен {response.status_code}"

        with allure.step("Проверить сообщение об отсутствии результатов"):
            body = response.text.lower()
            assert (
                "не прин" in body or "введите" in body or "результат" in body or "ничего" in body
            ), f"Ожидалось сообщение об отсутствии результатов. Фрагмент: {body[:200]}"

    @allure.title("Негативный: неподдерживаемый метод POST для поиска отклонён")
    @pytest.mark.api
    def test_wrong_method_for_search(self, api_session: requests.Session, api_base_url: str, search_query: str) -> None:
        with allure.step(f"POST {api_base_url}/search?q={search_query}"):
            response = api_session.post(f"{api_base_url}/search", params={"q": search_query}, timeout=20)

        with allure.step("Проверить отклонение (404/405/403) или пустую выдачу"):
            body = response.text.lower()
            is_rejected = response.status_code in (404, 405, 403)
            is_empty = response.status_code == 200 and "товар" not in body
            assert is_rejected or is_empty, f"POST вернул неожиданный успешный ответ: {response.status_code}"
