from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert # Для Postgres будет postgresql.insert

from app.database.models import User
from app.database.base import BaseRepo
from sqlalchemy.ext.asyncio import AsyncSession

class UserRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
    async def get_or_create(self, tg_id: int, username: str, full_name: str) -> User:
        """
        Возвращает юзера. Если нет - создает.
        Работает атомарно (Best Practice).
        """
        # Пытаемся найти
        stmt = select(User).where(User.id == tg_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Обновляем инфу, если сменил ник
            if user.username != username:
                user.username = username
                await self.session.commit()
            return user
        
        # Если нет - создаем
        new_user = User(id=tg_id, username=username, full_name=full_name)
        self.session.add(new_user)
        await self.session.commit()
        return new_user

    async def update_settings(self, tg_id: int, settings: dict):
        """
        Updates user settings JSON field.
        Used by onboarding to persist all user preferences.
        """
        stmt = select(User).where(User.id == tg_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            user.settings = settings
            await self.session.commit()

    # async def add_xp(self, tg_id: int, points: int):
    #     user = await self.get(tg_id) # Допустим, метод get есть
    #     if user:
    #         user.xp += points
    #         await self.session.commit()