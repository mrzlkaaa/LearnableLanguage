# Анализ: Telegram UX / Карточки / Навигация

## Дата: 2026-05-01
## Автор: Планировщик (Planner Agent)

---

## 1. Критические проблемы

### 1.1 Карточки — некорректная навигация и позиция

**Файл:** `backend/app/handlers/user/words_learning.py`

**Проблема в `get_next_card()`:**
```python
async def get_next_card(state: FSMContext, direction: int = 1):
    data = await state.get_data()
    card_counter = data.get("card_counter", None)

    if card_counter is not None:
        if card_counter == len(data["words"]) - 1:
            return None  # ← При выходе за границу возвращает None, но UI не обрабатывает!
        
        if direction and card_counter < len(data["words"]) - 1:
            card_counter += 1
        elif not direction and card_counter > 0:
            card_counter -= 1
    else:
        card_counter = 0  # ← При первом вызове не сохраняет в state!
    
    await state.update_data(card_counter=card_counter)
    # ↑ Асинхронный update_data НЕ гарантирует что следующий вызов получит обновлённое значение
    # Если два callback придут почти одновременно — race condition
```

**Симптомы:**
- При достижении конца списка возвращается `None` → показывается "Карточки закончились"
- Но кнопка "Следующая" остаётся активной и при нажатии снова показывает то же сообщение
- Позиция не отображается ("Карточка 3 из 10")

**Следствие:** Юзер не понимает где он в списке, и что "закончилось" — это нормально.

---

### 1.2 Дублирование слов при неправильном ответе

**Файл:** `backend/app/handlers/user/words_learning.py:113`

```python
await state.update_data(
    words=data["words"] + [word for word in data["words"] if word.word_id == callback_data.word_id]
)
```

**Проблемы:**
1. **O(N²) сложность** — для списка из 35 слов делается filter на каждый неправильный ответ
2. **Дубликаты** — слово добавляется в конец, но не удаляется из текущей позиции
3. **Утечка памяти** — при 10 ошибках слово будет в списке 11 раз

---

### 1.3 Race condition в асинхронном обновлении state

```python
await state.update_data(card_counter=card_counter)
# Между этой строкой и следующим callback — нет гарантии что данные уже записаны
```

**Если два callback придут почти одновременно:**
1. Callback A: card_counter=2, сохраняет 3
2. Callback B: card_counter=2 (старые данные!), сохраняет 3 ← потеря данных

---

## 2. Проблемы с клавиатурой / навигацией

### 2.1 Нет индикации позиции в UI

**Текущий UI:**
```
🇬🇧 HELLO [həˈloʊ]
🇷🇺 Привет

Контекст: "He said ___ to me"
(Он сказал мне ___)

Кнопки:
[Предыдущая] [Следующая]
[В меню изучения слов]
```

**Нет:**
- "Карточка 3 из 10"
- Прогресс-бар
- Визуального указания что это последняя карточка

### 2.2 Предыдущая не деактивируется на первой карточке

**Файл:** `backend/app/keyboards/learning/for_words.py`

```python
def get_card_navigation(word_id):
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="Предыдущая ⬅️",
        callback_data=WordCardQuizCallback(
            word_id=word_id,
            direction=0  # ← Всегда active! Нет проверки "если это первая карточка"
        )
    )
```

**Проблема:** На первой карточке кнопка "Предыдущая" активна, но при нажатии... что происходит? По логике `direction=0` значит "назад", но карточки закончились. Возвращает `None`?

---

### 2.3 "Назад" не сохраняет позицию

**Flow:**
1. Юзер на карточке 5 из 10
2. Нажимает "В меню изучения слов" → `vocab_menu_inline`
3. Возвращается в меню
4. Снова выбирает "Через карточки"
5. Начинает с карточки 1, не с 5!

**Причина:** В `words_learning_menu`:
```python
await state.update_data(
    card_counter=None  # ← Сбрасывает при уходе в меню
)
```

---

## 3. Проблемы с состояниями (States)

### 3.1 Смешивание состояний и данных

```python
# В words_learning_menu:
await state.update_data(
    words=words,
    user_id=user_id
)
# Это данные, но где карточка? counter сбрасывается в vocab_menu
```

**State machine размазана:**
- `card_counter` в FSM data, но не в LearningStates
- История navigation в `history` и `history_data`, но не связана с позицией карточек

### 3.2 Неиспользуемый State `reading_quiz`

```python
class LearningStates(StatesGroup):
    learning = State()
    vocabulary = State()    # ← Используется
    reading_quiz = State()  # ← Нигде не используется!
```

---

## 4. Архитектурные проблемы

### 4.1 `handle_callback` связывает все хендлеры

**Файл:** `backend/app/handlers/general.py`

```python
async def handle_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data == "back":
        history, history_data = await load_histiory(state)
    else:
        callback_data = callback.data
        history, history_data = await update_history(state, callback_data)
        await state.update_data(
            history=history,
            history_data=history_data
        )
```

**Проблемы:**
- Все callback проходят через одну точку — coupling
- History tracking хрупкий: если `callback.data == "back"` — не обновляет ничего
- Нет TTL для history, будет расти бесконечно

### 4.2 Сервис WordsLearningService создаётся каждый раз заново

```python
# В words_learning_menu:
wls = kwargs["words_service"]
```

**Проблема:** Это создаётся в хендлере, но если user_repo не передан через middleware — будет ошибка.

---

## 5. UX/UI проблемы высокого уровня

### 5.1 Нет фидбека при загрузке

**Flow:**
1. Юзер нажал "Через карточки"
2. Бот показывает сообщение без индикации загрузки
3. Если слов нет — долгое ожидание

**Нет:**
- "Загружаю карточки..."
- Spinner
- Лоадера

### 5.2 Нет адаптации под размер экрана

Все сообщения текстовые, нет оптимизации под мобильные устройства (QRSS, compact mode).

### 5.3 "Карточки закончились" — не информативно

```python
text = f"<b>Карточки для изучения закончились</b>\nДождись новых или переходи к другим секциям, удачи!"
```

**Проблемы:**
- Не показывает статистику: сколько карточек пройдено, сколько правильно/неправильно
- "Дождись новых" — пассивный, юзер не знает когда появятся
- Нет CTA (call to action): "Хочешь повторить?" / "Пройти ещё раз?"

---

## 6. Приоритизация доработок

### 🔴 P0 — Критично (блокирует usability)

| Проблема | Файл | Описание |
|----------|------|----------|
| Дублирование слов при ошибке | `words_learning.py:113` | O(N²) + утечка памяти |
| Нет позиции в UI | `for_words.py` | Юзер не знает где он |
| Race condition card_counter | `words_learning.py` | Потеря данных при параллельных callback |

### 🟡 P1 — Высокий приоритет (сильно влияет на UX)

| Проблема | Файл | Описание |
|----------|------|----------|
| Кнопка "Предыдущая" всегда активна | `for_words.py` | Делает невозможное действие валидным |
| "Назад" не сохраняет позицию | `words_learning.py` | Потеря прогресса |
| "Карточки закончились" без статистики | `for_words.py` | Потеря контекста |

### 🟢 P2 — Средний приоритет (улучшение)

| Проблема | Файл | Описание |
|----------|------|----------|
| History tracking хрупкий | `general.py` | Рост памяти, coupling |
| Нет лоадера | `words_learning.py` | юзер не понимает что происходит |
| reading_quiz не используется | `states.py` | Мусорный код |

---

## 7. Рекомендуемые направления доработок

### 7.1 Карточное взаимодействие — новый дизайн

**Предложение:** Вместо inline keyboard с кнопками — использовать **Inline Query + Switch Inline** для Telegram Mini App или **InlineKeyboard с pager**:

```python
# Новый подход: показывать прогресс
text = f"""🇬🇧 <b>{word.word_text.upper()}</b>

📍 Карточка {current + 1} из {total}

🇷🇺 {word.translation}"""
```

### 7.2 Вынос карточной логики в отдельный сервис

```python
# Создать CardNavigationService
class CardNavigator:
    def __init__(self, state: FSMContext):
        self.state = state
    
    async def get_current_index() -> int
    async def get_word() -> WordCardDTO
    async def next() -> WordCardDTO | None
    async def previous() -> WordCardDTO | None
    async def reinsert_failed_word(word_id) -> None
    async def get_progress() -> tuple[int, int]  # (current, total)
```

### 7.3 Оптимизация дублирования слов

**Текущий код:**
```python
words=data["words"] + [word for word in data["words"] if word.word_id == callback_data.word_id]
```

**Исправить на:**
```python
# Добавить в начало списка, не в конец
failed_word = next((w for w in data["words"] if w.word_id == callback_data.word_id), None)
if failed_word:
    words = [failed_word] + [w for w in data["words"] if w.word_id != callback_data.word_id]
else:
    words = data["words"]
```

---

## 8. Итог

**Главные проблемы, блокирующие хороший UX:**

1. **Навигация** — нет позиции, нет прогресс-бара, кнопки не деактивируются
2. **Память** — дублирование слов при ошибках
3. **Concurrency** — race condition в card_counter
4. **Информативность** — "закончилось" без статистики и CTA

**Направление работы:**
- Сначала пофиксить P0 (дублирование, race condition)
- Потом добавить прогресс-бар и позицию (P1)
- Потом рефакторинг в отдельный CardNavigator service (P2)

---

_Анализ подготовлен планировщиком для Никиты_
_Дата: 2026-05-01_