import pandas as pd
from src.views import greets, cards, top_category, filter_date


from unittest.mock import patch

def test_greets():
    result = greets()
    assert result in ["Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи"]


def test_cards():
    df = pd.DataFrame({
        "Номер карты": ["1111", "1111", "2222"],
        "Сумма операции": [-100, -200, -300]
    })

    result = cards(df)

    assert isinstance(result, list)
    assert "last_digits" in result[0]
    assert "total_spent" in result[0]
    assert "cashback" in result[0]


def test_top_category():
    df = pd.DataFrame({
        "Дата операции": pd.to_datetime(["2021-01-01"]),
        "Категория": ["Супермаркеты"],
        "Описание": ["Покупка"],
        "Сумма операции": [-500]
    })

    result = top_category(df)

    assert isinstance(result, list)
    assert "category" in result[0]


@patch("src.views.read_excel")
def test_filter_date(mock_read):
    mock_read.return_value = pd.DataFrame({
        "Дата операции": ["01.01.2021 10:00:00"],
        "Сумма операции": [-100]
    })

    result = filter_date("2021-01-10 10:00:00")

    assert not result.empty