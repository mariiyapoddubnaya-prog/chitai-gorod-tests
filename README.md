# Автотесты для веб-приложения "Читай-город"

Дипломный проект по автоматизации тестирования.

##  Стек технологий
- Python 3.9+
- pytest
- requests (для API тестов)
- playwright (для UI тестов)
- allure-pytest (для формирования отчетов)
- python-dotenv (для управления переменными окружения)

##  Структура проекта
- `pages/` — реализация паттерна Page Object для UI-тестов.
- `tests/api/` — автоматизированные API-тесты.
- `tests/ui/` — автоматизированные UI-тесты.
- `conftest.py` — глобальные фикстуры (инициализация браузера, загрузка конфигов).
- `.env` — конфигурационные переменные (URL, тестовые данные).

##  Установка и запуск

1. Клонируйте репозиторий и перейдите в папку проекта:
   git clone https://github.com/ВАШ_НИК/chitai-gorod-tests.git
   cd chitai-gorod-tests   
2. Запуск тестов:
    Все тесты: pytest
    Только UI тесты: pytest -m "ui"
    Только API тесты: pytest -m "api"
    С формированием отчета Allure: pytest --alluredir=allure-results
    Просмотр отчета Allure: allure serve allure-results
   
