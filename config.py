import pathlib

BASE_PATH = pathlib.Path(__file__).parent

EXCEL_PATH = BASE_PATH / "data" / "operations.xlsx"
LOG_PATH = BASE_PATH / "logs"
ENV_PATH = BASE_PATH / ".env"
SETTINGS_PATH = BASE_PATH / "user_settings.json"
