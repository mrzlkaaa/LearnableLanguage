from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from app.config import config

from sqlalchemy.ext.asyncio import AsyncSession

# Создаем асинхронный движок
# echo=True полезно для отладки (видим SQL запросы в консоли)
engine = create_async_engine(
    url=config.DB_URL, 
    echo=config.LOG_LEVEL == "DEBUG"
)

# Фабрика сессий. Используем ее в Dependency Injection (DI).
async_session = async_sessionmaker(
    engine, 
    expire_on_commit=False, 
    autoflush=False
)

# Базовый класс для всех моделей
# AsyncAttrs добавляет удобные асинхронные методы (типа .awaitable_attrs)
class Base(AsyncAttrs, DeclarativeBase):
    pass

# Функция инициализации (создает таблицы при старте)
# В продакшене лучше использовать Alembic миграции!
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class BaseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session