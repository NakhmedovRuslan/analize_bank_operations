import logging

from config import LOG_PATH
from src.views import read_excel

logger = logging.getLogger()
file_handler = logging.FileHandler(
    LOG_PATH / "services.log", encoding="utf-8", mode="w"
)
file_formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def search(data_for_search: str) -> str:
    """Функция поиска в DF по ключевому слову в столбце "Категория" или "Описание" """
    logger.info(f"{search.__name__}: start")
    df = read_excel()

    # фильтр с учётом проверки на регистр, поиска по подстроке
    filtered_category = df[
        df["Категория"].astype(str).str.contains(data_for_search, case=False)
    ]

    if not filtered_category.empty:
        filtered_category_json = filtered_category.to_json(
            orient="records", force_ascii=False, indent=4
        )
        logger.debug(f"{search.__name__}: filtered by category.")
        logger.info(f"{search.__name__}: ok")
        return filtered_category_json

    filtered_description = df[
        df["Описание"].astype(str).str.contains(data_for_search, case=False)
    ]
    filtered_description_json = filtered_description.to_json(
        orient="records", force_ascii=False, indent=4
    )
    logger.debug(f"{search.__name__}: filtered by description.")
    logger.info(f"{search.__name__}: ok")
    return filtered_description_json


print(search("Супермаркеты"))
