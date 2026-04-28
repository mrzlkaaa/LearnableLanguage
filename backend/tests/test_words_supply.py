import pytest
from sqlalchemy import select, func, desc
from app.database.base import async_session
from sqlalchemy.orm import joinedload 

from app.database.models import Word, UserWord, User

@pytest.fixture()
async def session():
    async with async_session() as session:
        yield  session

@pytest.mark.asyncio
async def test_avaliable_words(session):
    buffer = 10

    uw = (
        select(User, func.count(UserWord.word_id).label("vocab_size"))
        .join(User.vocabulary)
        .join(Word, UserWord.word_id == Word.id)
        .where(Word.cefr_level == "B2")
        .group_by(User.id)
        .order_by(desc("vocab_size"))
        .limit(1)
    )
    result = await session.execute(uw)
    row = result.first()
    
    current_user_count = 0
    if row:
        current_user_count = row[1]
        

    w = (
        select(func.count(Word.id).label("vocab_size"))
        .where(Word.cefr_level == "B2")
        .limit(1)
    )
    result = await session.execute(w)
    row = result.first()
    
    total_words = 0
    if row:
        total_words = row[0]

    current_count = total_words - current_user_count
    to_generate = buffer - current_count
    print(to_generate)

    assert 0