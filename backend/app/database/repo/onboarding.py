from sqlalchemy import select, func
from app.database.models import PlacementTestQuestion
from app.database.base import BaseRepo


class OnboardingRepo(BaseRepo):
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
                "correct": q.data.get("correct", q.data.get("correct_index", 0)),
                "level": q.difficulty_level
            }
            for q in questions
        ]
