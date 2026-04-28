from app.core.clients import GeminiClient
from app.core.dtos import AIFeedbackDTO, GeneratedWordDTO
from app.core.prompts import SYSTEM_PERSONA, CHECK_VOCABULARY_PROMPT, NEW_WORD
import random
import string

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

TOPICS = [
    # --- Быт и Жизнь ---
    "Home & Housing",       # A1: Room -> C2: Mortgage
    "Food & Cooking",       # A1: Apple -> C2: Culinary
    "Health & Body",        # A1: Leg -> C2: Diagnosis
    "Shopping & Money",     # A1: Buy -> C2: Expenditure
    "Clothing & Fashion",   # A1: Shirt -> C2: Textile
    
    # --- Общество и Люди ---
    "Personality & Mood",   # A1: Happy -> C2: Apprehensive
    "Relationships",        # A1: Friend -> C2: Acquaintance
    "Communication",        # A1: Talk -> C2: Negotiate
    "Law & Crime",          # A1: Police -> C2: Litigation
    
    # --- Мир и Работа ---
    "Work & Career",        # A1: Job -> C2: Tenure
    "Technology",           # A1: Computer -> C2: Algorithm
    "Environment",          # A1: Tree -> C2: Biodiversity
    "Travel & Transport",   # A1: Bus -> C2: Itinerary
    "Arts & Media",         # A1: Book -> C2: Narrative
    
    # --- Абстракции (Важно!) ---
    "Time & History",       # A1: Day -> C2: Era
    "Thoughts & Ideas",     # A1: Think -> C2: Conceptualize
    "Global Issues"

    "Phrasal Verbs",
    "Idioms & Phrases",
    "Linkers & Connectors "
]

class AITutorService:
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client

    async def generate_new_vocabulary(self, level: str) -> GeneratedWordDTO | None:
        """
        Генерирует слово, используя двойную энтропию (Случайная тема + Случайная буква).
        """
        # 1. Выбираем случайную тему
        random_topic = random.choice(TOPICS)
        
        # 2. Выбираем случайную стартовую букву (чтобы точно избежать повторов)
        random_letter = random.choice(string.ascii_lowercase) # 'a' - 'z'
        prompt = NEW_WORD.format(
            level=level,
            random_topic=random_topic,
            random_letter=random_letter.upper()
        )
        
        res = await self.client.generate_new_word(SYSTEM_PERSONA, prompt)

        try:
            return GeneratedWordDTO(**res)
        except Exception as e:
            print(f"Error parsing generated word: {e}")
            return None