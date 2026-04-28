import logging
import sys
from app.config import config

def setup_logger():
    """
    Настраивает формат логов.
    В продакшене (Docker) лучше писать в stdout (StreamHandler).
    """
    # Формат: [Время] [Уровень] [Имя Модуля]: Сообщение
    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=log_format,
        handlers=[
            logging.FileHandler("brobot.log", mode="w+"),  # Handler to write to a file (overwrites file on each run)
            logging.StreamHandler(sys.stdout)  # Handler to write to the console (stdout)
        ]
    )
    
    # Убираем шум от библиотек, если нужно
    logging.getLogger("aiogram.event").setLevel(logging.INFO)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return logging