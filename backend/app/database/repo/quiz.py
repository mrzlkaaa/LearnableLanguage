from sqlalchemy import select, func
from app.database.models import FCEQuestion
from .base import BaseRepo

class OnboardingRepo(BaseRepo):
    async def get_random_question(self, part_type: str = None) -> FCEQuestion | None:
        """
        Берет случайный вопрос из базы.
        """
        stmt = select(FCEQuestion)
        
        if part_type:
            stmt = stmt.where(FCEQuestion.part_type == part_type)
            
        # func.random() работает в SQLite и Postgres
        stmt = stmt.order_by(func.random()).limit(1)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()