from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.client.session.aiohttp import AiohttpSession
from app.config import config

session = AiohttpSession()


async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot"),
        # BotCommand(command="help", description="Get help information"),
        # BotCommand(command="menu", description="View the main menu options")
    ]
    await bot.set_my_commands(commands)

# Инициализация бота с дефолтным парсингом HTML
bot = Bot(
    token=config.BOT_TOKEN.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session
)

# Хранилище состояний (FSM). 
# Для продакшена лучше RedisStorage, для MVP сойдет MemoryStorage (в RAM).
storage = MemoryStorage()

dp = Dispatcher(storage=storage)