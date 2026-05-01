# План проекта — Sprint 1

## Цель

Исправить критические P0 баги + сделать полноценный онбординг для новых юзеров (запуск в работу фуллстаку).

## Шаги

```
БЛОК A: Исправление критических проблем (3-4ч)
├── A1: O(N²) дублирование слов при ошибке
├── A2: Race condition card_counter (FSM atomic)
├── A3: Прогресс-бар "Карточка 3 из 10"
└── A4: Деактивировать "Предыдущая" на первой карточке

БЛОК C: Zero-Debt Gate (2-3ч)
└── C1: Блокировка новых слов при SRS queue > 15

БЛОК O: Полноценный онбординг (4-6ч)
├── O1: Новые FSM states (words_per_day, reminder_frequency, active_hours, topics)
├── O2: UI Flow (7 шагов)
├── O3: Новые keyboards (words_per_day, reminder_frequency, active_hours, topics)
├── O4: Placement test — включить (был закомментирован)
└── O5: Сохранение всех настроек в user.settings
```

## ДЕТАЛЬНАЯ СПЕЦИФИКАЦИЯ

---

### A1: O(N²) дублирование слов

**Файл:** `backend/app/handlers/user/words_learning.py` ~строка 113

**Текущий код (НЕВЕРНО):**
```python
elif callback_data.is_correct == False:
    await state.update_data(
        words=data["words"] + [word for word in data["words"] if word.word_id == callback_data.word_id]
    )
```
- `list comprehension` по ВСЕМУ списку на КАЖДУЮ ошибку = O(N²)
- При 10 словах и 3 ошибках → 40 слов в списке

**Решение:**
```python
# Вариант 1: Вставка в начало + удаление из текущей позиции
elif callback_data.is_correct == False:
    failed_word = next(w for w in data["words"] if w.word_id == callback_data.word_id)
    words_list = [failed_word] + [w for w in data["words"] if w.word_id != callback_data.word_id]
    await state.update_data(words=words_list, card_counter=0)

# Вариант 2 (лучше): Не дублировать вручную — box=1 автоматически вернёт слово в следующий review
# Просто убрать этот код вообще.
```

---

### A2: Race condition card_counter

**Файл:** `backend/app/handlers/user/words_learning.py`, функция `get_next_card()`

**Проблема:**
```python
data = await state.get_data()       # READ
# ...логика...
await state.update_data(...)        # WRITE
# Между read и write — другой вызов может изменить state
```

**Решение:** Добавить проверку границ ДО изменения:
```python
async def get_next_card(state: FSMContext, direction: int = 1) -> WordCardDTO | None:
    data = await state.get_data()
    words = data.get("words", [])
    card_counter = data.get("card_counter", 0)
    
    new_counter = card_counter + direction if direction == 1 else card_counter - 1
    
    # Границы — проверяем ДО изменения
    if new_counter < 0 or new_counter >= len(words):
        return None
    
    await state.update_data(card_counter=new_counter)
    return words[new_counter]
```

---

### A3: Прогресс-бар

**Файл:** `backend/app/keyboards/learning/for_words.py`

**В `get_word_card()` и `get_translation_card()` добавить:**
```python
def get_word_card(word, current: int = 0, total: int = 0):
    if word:
        progress = f"🔢 Карточка {current + 1} из {total}\n"
        progress_bar = "".join(["🟩" if i <= current else "🟦" for i in range(total)])
        text = f"{progress}{progress_bar}\n\n" + original_text
```

**В `words_learning.py`:**
```python
# При инициализации
await state.update_data(
    card_counter=0,
    total_words=len(words),
    current_position=0
)

# При навигации
text, kb = get_word_card(word, current=data["current_position"], total=data["total_words"])
```

---

### A4: Деактивировать "Назад"

**Файл:** `backend/app/keyboards/learning/for_words.py`, `get_card_navigation()`

```python
def get_card_navigation(word_id, current: int = 0, total: int = 0):
    builder = InlineKeyboardBuilder()
    
    prev_callback = WordCardQuizCallback(word_id=word_id, direction=0) if current > 0 else "noop"
    prev_text = "⬅️ Назад" if current > 0 else "⬅️ Начало"
    
    builder.button(text=prev_text, callback_data=prev_callback)
    # ...следующая...
```

---

### C1: Zero-Debt Gate

**Файл:** `backend/app/core/services/words_learning.py`

```python
async def get_new_global_words(self, user_id: int, num_words: int = 100):
    # 🆕 Проверка SRS queue
    srs_queue_count = await self.vocab.get_srs_queue_count(user_id)
    ZERO_DEBT_THRESHOLD = 15
    
    if srs_queue_count > ZERO_DEBT_THRESHOLD:
        logger.info(f"Zero-Debt gate: user {user_id} has {srs_queue_count} words pending")
        return None
```

**Новый метод в `backend/app/database/repo/vocabulary.py`:**
```python
async def get_srs_queue_count(self, user_id: int) -> int:
    from datetime import datetime
    stmt = select(func.count(UserWord.id)).where(
        UserWord.user_id == user_id,
        UserWord.box < MAX_BOX_LEVEL,
        UserWord.next_review <= datetime.now()
    )
    result = await self.session.execute(stmt)
    return result.scalar() or 0
```

**UI feedback при блокировке:**
```python
if not new_words:
    srs_queue = await wls.get_srs_queue_count(user_id)
    await callback.message.edit_text(
        f"🔒 <b>Новые слова заблокированы!</b>\n\n"
        f"У тебя {srs_queue} слов ждут повторения. "
        f"Сначала повтори их!\n\n💡 Нажми 'Через карточки' → там будут слова на повтор"
    )
```

---

### O1-O5: Онбординг (7 шагов)

**Новые FSM states (`states.py`):**
```python
class OnboardingStates(StatesGroup):
    waiting_for_goal = State()
    waiting_for_schedule = State()
    waiting_for_words_per_day = State()      # 🆕
    waiting_for_reminder_frequency = State() # 🆕
    waiting_for_active_hours = State()       # 🆕
    waiting_for_topics = State()             # 🆕
    placement_test = State()
```

**UI Flow:**
```
/start → [Goal] → [Words/day] → [Reminder freq] → [Active hours] → [Topics] → [Placement test] → [Result + save]
```

**Новые keyboards (`for_onboarding.py`):**
```python
def get_words_per_day_menu() -> InlineKeyboardMarkup:
    # 3 / 5 / 10 слов

def get_reminder_frequency_menu() -> InlineKeyboardMarkup:
    # 1 / 2 / 3 раза в день

def get_active_hours_menu() -> InlineKeyboardMarkup:
    # 🌅 9:00 / ☀️ 14:00 / 🌙 20:00

def get_topics_menu() -> InlineKeyboardMarkup:
    # ☑️ Technology / ☑️ Business / ☑️ Travel / ... + "✅ Готово"
```

**Сохранение в БД (`user.py` repo):**
```python
settings = {
    "goal": data["goal"],
    "words_per_day": int(data["words_per_day"]),
    "reminder_frequency": int(data["reminder_frequency"]),
    "active_hours": data["active_hours"],
    "topics": data["topics"],
    "cefr_level": final_level,
    "onboarding_completed": True
}
await user_repo.update_settings(user_id, settings)
```

**Placement test — включить** (код есть, был закомментирован):
- Раскомментировать логику загрузки вопросов из `PlacementTestQuestion`
- Подключить `send_question()` с реальными данными из БД

---

## Файлы для изменения

| Файл | Задачи |
|------|--------|
| `backend/app/handlers/user/words_learning.py` | A1, A2, A3 context |
| `backend/app/keyboards/learning/for_words.py` | A3 progress bar, A4 |
| `backend/app/core/services/words_learning.py` | C1 Zero-Debt gate |
| `backend/app/database/repo/vocabulary.py` | `get_srs_queue_count()` |
| `backend/app/handlers/user/onboarding.py` | O2 flow, O4 placement test |
| `backend/app/states.py` | O1 FSM states |
| `backend/app/keyboards/for_onboarding.py` | O3 keyboards |
| `backend/app/database/repo/user.py` | O5 `update_settings()` |

---

## Ожидаемый результат

- [ ] A1: При ошибке слово не дублируется N раз
- [ ] A2: Race condition невозможен
- [ ] A3: UI показывает "Карточка 3 из 10" + прогресс-бар
- [ ] A4: "Назад" деактивирована на первой карточке
- [ ] C1: Zero-Debt блокирует новые слова при SRS > 15
- [ ] O: 7-шаговый онбординг работает, настройки сохраняются в БД

## Риски

- Placement test был закомментирован — нужно проверить что БД модель `PlacementTestQuestion` существует
- Zero-Debt может быть слишком строгим порогом — 15 слов ожидания это норма или нужно 10?

---

_Обновлено: 2026-05-02_
_Ждёт команду "запускай"_
