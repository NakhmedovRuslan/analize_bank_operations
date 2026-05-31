import pandas as pd
from src.reports import spending_by_category


def test_spending_by_category():
    df = pd.DataFrame({
        "Дата операции": ["01.01.2021"],
        "Категория": ["Супермаркеты"],
        "Сумма операции": [-100]
    })

    result = spending_by_category(df, "Супермаркеты", "2021-02-01 10:00:00")

    assert not result.empty
    assert "Категория" in result.columns