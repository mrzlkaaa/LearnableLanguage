from sqlalchemy import select, func
from app.database.models import FCEQuestion, PlacementTestQuestion
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

    async def get_placement_questions(self, limit: int = 10) -> list[dict]:
        """
        Returns placement test questions as dicts for onboarding.
        """
        stmt = select(PlacementTestQuestion).order_by(func.random()).limit(limit)
        result = await self.session.execute(stmt)
        questions = result.scalars().all()
        return [
            {
                "q": q.text,
                "opts": q.data.get("options", []),
                "correct": q.data.get("correct_index", 0),
                "level": q.difficulty_level
            }
            for q in questions
        ]