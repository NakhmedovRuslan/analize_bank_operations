import datetime
import json
import logging
import os
import time
from typing import Any, Hashable

import pandas as pd
import requests
from dotenv import load_dotenv

from config import EXCEL_PATH, LOG_PATH, SETTINGS_PATH

load_dotenv()

logger = logging.getLogger()
file_handler = logging.FileHandler(LOG_PATH / "views.log", encoding="utf-8", mode="w")
file_formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def read_excel() -> pd.DataFrame:
    """Функция чтения EXCEL файла. Возвращает DataFrame."""
    logger.info(f"{read_excel.__name__}: start")
    df = pd.read_excel(EXCEL_PATH)
    if df.empty:
        logger.error(f"{read_excel.__name__}: excel file not found")
        raise FileNotFoundError("Excel File Not Found")
    else:
        logger.info(f"{read_excel.__name__}: ok")
        return df


def greets() -> str:
    """Функция приветствия пользователя в зависимости от текущего времени."""
    logger.info(f"{greets.__name__}: start")
    current_time = datetime.datetime.now()
    greetings = ""

    if 6 <= current_time.hour < 12:
        greetings = "Доброе утро"
    elif 12 <= current_time.hour < 18:
        greetings = "Добрый день"
    elif 18 <= current_time.hour < 23:
        greetings = "Добрый вечер"
    else:
        greetings = "Доброй ночи"

    logger.info(f"{greets.__name__}: ok")
    return greetings


def filter_date(date: str) -> pd.DataFrame:
    """
    Функция принимает дату в строковом значении с форматом ГГГГ-ММ-ДД ЧЧ:ММ:СС.
    Возвращает отфильтрованный DataFrame с 1-го числа месяца, указанного в дате, до даты в вызове функции.
    """

    logger.info(f"{filter_date.__name__}: start")

    date_obj = datetime.datetime.strptime(
        date, "%Y-%m-%d %H:%M:%S"
    )  # преобразование строки с датой в datetime
    first_day = date_obj.replace(
        day=1, hour=0, minute=0, second=0
    )  # меняю дату первого числа месяца

    df = read_excel()
    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"], format="%d.%m.%Y %H:%M:%S"
    )  # меняю дату в датафрейме на формат datetime с форматом.

    # фильтр по дате
    filter_by_date = df[
        (df["Дата операции"] >= first_day) & (df["Дата операции"] <= date_obj)
    ]

    # фильтр только по отрицательным значениям
    filtered_df = filter_by_date[filter_by_date["Сумма операции"] < 0]
    logger.info(f"{filter_date.__name__}: ok")
    return filtered_df


def cards(filtered_df: pd.DataFrame) -> list[dict[Hashable, Any]]:
    """Функция принимает отфильрованный DataFrame по датам.
    Возвращает уникальный список номеров карт в заданном периоде"""
    logger.info(f"{cards.__name__}: start")
    # создание датафрейма по расходам (колонки номер карты и сумма операции)
    expenses = (
        filtered_df.groupby("Номер карты")["Сумма операции"].sum().abs().reset_index()
    )

    # добавил колонку кэшбек (1 рубль с каждых 100р потраченных)
    expenses["Кэшбек"] = round((expenses["Сумма операции"] / 100), 2)

    expenses = expenses.rename(
        columns={
            "Номер карты": "last_digits",
            "Сумма операции": "total_spent",
            "Кэшбек": "cashback",
        }
    )

    cards_list = expenses.to_dict(orient="records")
    logger.info(f"{cards.__name__}: ok")
    return cards_list


def top_category(filtered_df: pd.DataFrame) -> list[dict[Hashable, Any]]:
    """Функция принимает отфильрованный DataFrame по датам.
    Возвращает топ 5 категорий по расходам."""
    logger.info(f"{top_category.__name__}: start")
    category_sum = (
        filtered_df.groupby(["Дата операции", "Категория", "Описание"])[
            "Сумма операции"
        ]
        .sum()
        .sort_values(ascending=True)
        .head(5)
        .reset_index()
    )
    category_sum = category_sum.rename(
        columns={
            "Дата операции": "date",
            "Сумма операции": "amount",
            "Категория": "category",
            "Описание": "description",
        }
    )

    category_sum = category_sum[["date", "amount", "category", "description"]]

    category_sum["date"] = category_sum["date"].dt.strftime("%d-%m-%Y")
    top_transactions = category_sum.to_dict(orient="records")
    logger.info(f"{top_category.__name__}: ok")
    return top_transactions


# ФУНКЦИИ ДЛЯ ОБРАБОТКИ АПИ
def currency_values(filename: str) -> str | list[Any]:
    """Функция API запроса на вывод курса валют на текущую дату."""
    logger.info(f"{currency_values.__name__}: start")
    api_key = os.getenv("API_KEY")

    with open(filename) as f:
        data = json.load(f)
        currency = data["user_currencies"]

        all_currency_data = []
        for elem in currency:
            url = (
                f"https://www.alphavantage.co/query?"
                f"function=CURRENCY_EXCHANGE_RATE&"
                f"from_currency={elem}&"
                f"to_currency=RUB&"
                f"apikey={api_key}"
            )

            try:
                response = requests.get(url)
                response.raise_for_status()
                logger.info(
                    f"{currency_values.__name__}: status code {response.status_code}"
                )
                currency_data = response.json()
                all_currency_data.append(currency_data)
                time.sleep(1)

            except requests.exceptions.RequestException as err:
                logger.error(f"{currency_values.__name__}: An error occurred, {err}")
                return "An error occurred. Please try again later."

    total_currencies_rates = []
    for elem in all_currency_data:
        total_currencies_rates.append(
            {
                "currency": elem.get("Realtime Currency Exchange Rate").get(
                    "1. From_Currency Code"
                ),
                "rate": round(
                    float(
                        elem.get("Realtime Currency Exchange Rate").get(
                            "5. Exchange Rate"
                        )
                    ),
                    2,
                ),
            }
        )
        logger.info(f"{currency_values.__name__}: ok")
    return total_currencies_rates


def stock_500(filename: str) -> str | list[Any]:
    """Функция API запроса на вывод стоимости акций текущую дату."""
    logger.info(f"{stock_500.__name__}: start")
    api_key_stock = os.getenv("API_KEY_STOCK")

    with open(filename) as f:
        data = json.load(f)
        stocks = data["user_stocks"]

    all_stock_rates = []
    for elem in stocks:
        url = f"https://api.twelvedata.com/time_series?apikey={api_key_stock}&symbol={elem}&interval=1min&format=JSON"
        try:
            response = requests.get(url)
            response.raise_for_status()
            stock_data = response.json()
            all_stock_rates.append(stock_data)
        except requests.exceptions.RequestException as err:
            logger.error(f"{stock_500.__name__}: An error occurred, {err}")
            return "An error occurred. Please try again later."

    total_stock_rates = []
    for elem in all_stock_rates:
        total_stock_rates.append(
            {
                "stock": elem["meta"]["symbol"],
                "price": round(float(elem["values"][0]["close"]), 2),
            }
        )

    logger.info(f"{stock_500.__name__}: ok")
    return total_stock_rates


# MAIN ФУНКЦИЯ
def total_json(date: str) -> str | list[Any]:
    """Основная функция для запуска всех функций модуля views.py"""
    filtered = filter_date(date)
    result = {
        "greetings": greets(),
        "cards": cards(filtered),
        "top_transactions": top_category(filtered),
        "currency_rates": currency_values(str(SETTINGS_PATH)),
        "stock_prices": stock_500(str(SETTINGS_PATH)),
    }

    return json.dumps(result, indent=4, ensure_ascii=False)


print(total_json("2021-12-02 21:45:00"))
