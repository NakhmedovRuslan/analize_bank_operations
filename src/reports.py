import logging
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from config import LOG_PATH
from src.views import read_excel

logger = logging.getLogger()
file_handler = logging.FileHandler(LOG_PATH / "reports.log", encoding="utf-8", mode="w")
file_formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def log(filename: Optional[str] = None) -> Callable:
    """Декоратор записи в файл результата работы функции spending_by_category"""
    logger.info(f"{log.__name__}: start")

    def log_2_stage(func):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            if filename is None:
                logger.debug(f"{log.__name__}: filename = None")
                with open(LOG_PATH / "reports_result.csv", "w", encoding="utf-8") as f:
                    f.write(str(result))
                    logger.info(
                        f"{log.__name__}: result is written to logs/reports_result.csv"
                    )

            else:
                logger.debug(f"{log.__name__}: filepath = {filename}")
                with open(LOG_PATH / filename, "w", encoding="utf-8") as f:
                    f.write(str(result))
                    logger.info(f"{log.__name__}: result is written to {filename}")
            logger.info(f"{log.__name__}: ok")
            return result

        return wrapper

    return log_2_stage


@log(filename=None)
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    """Функция вывода трат по заданной пользователем категории в заданный период (дата-3 месяца)"""
    logger.info(f"{spending_by_category.__name__}: start")
    logger.debug(f"category: {category}, date: {date}")
    df = transactions

    if date is None:
        date = datetime.now()  # Если нет даты, берем текущую
    else:
        date = datetime.strptime(
            date, "%Y-%m-%d %H:%M:%S"
        )  # если дата установлена, приводим её к datetime

    date_minus_3_month = date - relativedelta(months=3)
    logger.debug(
        f"{spending_by_category.__name__}: dates = from {date_minus_3_month} to {date}"
    )

    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"], dayfirst=True
    )  # приводим дату в dataframe к datetime

    filtered_by_date_and_category = df[
        (df["Дата операции"] <= date)
        & (df["Дата операции"] >= date_minus_3_month)
        & (df["Категория"] == category)
    ]  # фильтр DF по начальной дате, по конечной дате,а так же по категории

    logger.info(f"{spending_by_category.__name__}: ok")

    return filtered_by_date_and_category


print(spending_by_category(read_excel(), "Супермаркеты", "2020-05-20 13:20:15"))
