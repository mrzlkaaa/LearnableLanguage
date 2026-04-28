from typing import List
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


#* ways to extend app
#   config folder
#   independent configs (db, tg and etc)
#   factory load all of them in main config.py via pydantic

class Settings(BaseSettings):
    # SecretStr скрывает значение при печати в логах (защита от утечек)
    BOT_TOKEN: SecretStr
    GEMINI_API_KEY: SecretStr
    
    # Автоматически распарсит строку "123,456" в список [123, 456]
    ADMIN_IDS: List[int]
    
    LOG_LEVEL: str = "INFO"
    DB_URL: str

    # Настройки чтения .env файла
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Игнорировать лишние переменные в файле
    )

# Инициализируем один раз. Если тут ошибка — бот не запустится.
config = Settings()