import pandas as pd
from src.services import search
from unittest.mock import patch


@patch("src.services.read_excel")
def test_search_by_category(mock_read):
    mock_read.return_value = pd.DataFrame({
        "Категория": ["Супермаркеты"],
        "Описание": ["Покупка хлеба"]
    })

    result = search("Супермаркеты")

    assert "Супермаркеты" in result