# Competitive Analysis — LearnableLanguage Bot

**Дата:** 2026-05-02  
**Ветка:** dev  
**Автор:** Планировщик

---

## 1. РЫНОЧНЫЙ КОНТЕКСТ

### 1.1 Search Signal
- Telegram bot + English learning: **высокая конкуренция**  
- Spaced repetition + AI generation: **ниша с потенциалом**
- 229,087 Telegram bot репозиториев на GitHub
- 21% созданы за последние 6 месяцев

### 1.2 Конкуренты найденные на GitHub

| Проект | ⭐ | Описание | SRS | AI | Telegram |
|--------|---|---------|-----|----|-----------|
| **retell** | 12 | Английский через短文背诵 + голос | ✅ | ❌ | ✅ |
| **VocabMaster (CyberSenpa1)** | ~5 | Интеллектуальный бот с адаптацией | ✅ | ❌ | ✅ |
| **english-vocabulary-trainer-bot** | 2 | SRS + TTS произношение | ✅ | ❌ | ✅ |
| **FlashCard_ecosystem** | 1 | AI-powered для Italian | ✅ | ✅ | ✅ |
| **nevermindybot** | 6 | Spaced reminder | ✅ | ❌ | ✅ |
| **Anki (open-source clones)** | 118+ | Anki-совместимые iOS клиенты | ✅ | ❌ | ❌ |

---

## 2. СРАВНИТЕЛЬНЫЙ АНАЛИЗ ФУНКЦИЙ

### 2.1 Матрица фич конкурентов

| Функция | **Duolingo** | **Anki** | **Memrise** | **Retell (TG)** | **Наш бот** |
|---------|:---:|:---:|:---:|:---:|:---:|
| **Обучение词汇** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **SRS (интервалы)** | ❌ (линейное) | ✅ (SM-2) | ✅ | ✅ | ✅ (6 уровней) |
| **AI-генерация слов** | ❌ | ❌ | ❌ | ❌ | ✅ Gemini |
| **Смена механики по уровню** | ❌ | ❌ | ❌ | ❌ | ✅ CSRS (план) |
| **Голос / Voice production** | ✅ | ❌ | ✅ | ✅ | ❌ (план D1) |
| **AI-проверка голоса** | ❌ | ❌ | ❌ | ❌ | ❌ (план D1) |
| **Контекстные диалоги** | ✅ (Stories) | ❌ | ❌ | ❌ | ❌ (план D2) |
| **Zero-Debt Rule** | ❌ | ❌ | ❌ | ❌ | ❌ (план C1) |
| **Accuracy Throttle** | ❌ | ❌ | ❌ | ❌ | ❌ (план C2) |
| **Production Lock (голос)** | ❌ | ❌ | ❌ | ❌ | ❌ (план C3) |
| **CEFR уровни** | ✅ | ❌ (ручная настройка) | ✅ | ❌ | ✅ |
| **Онбординг / Placement test** | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Streaks / привычка** | ✅ | ❌ | ✅ | ❌ | ❌ (план E1) |
| **Прогресс-бар уровня** | ✅ | ❌ | ✅ | ❌ | ❌ (план E2) |
| **Telegram Native** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Бесплатный** | ✅ (с рекламой) | ✅ (self-hosted) | ❌ (платная) | ✅ | ✅ |
| **Open Source** | ❌ | ✅ | ❌ | ❌ | ✅ |

### 2.2 Наши сильные стороны (уже реализовано)

1. **✅ AI-генерация через Gemini** — конкуренты делают это вручную или через API
2. **✅ 6-уровневая SRS** — даже Anki использует 6 уровней (Leitner scale)
3. **✅ CEFR уровни** — большинство ботов не имеют этого
4. **✅ Telegram native** — полный доступ к войс/текст
5. **✅ Онбординг** — placement test + анкетирование
6. **✅ Zero-sum approach с review-first** — уже частично реализовано

### 2.3 Наши слабые стороны (уже реализовано)

1. **❌ Нет смены механики по уровню** — Killer Feature из docx не реализована
2. **❌ Нет AI-проверки голоса** — Duolingo voice нет, Retell есть
3. **❌ Нет streaks/gamification** — удержание хуже чем у Duolingo
4. **❌ Нет "Zero Debt" gate** — можно набрать бесконечный долг
5. **❌ Нет Accuracy Throttle** — нет динамического лимита
6. **❌ UI карточек сырой** — анализ UX выявил критические баги

---

## 3. ДЕТАЛЬНЫЙ РАЗБОР КОНКУРЕНТОВ

### 3.1 Duolingo — Gold Standard

**Сильные стороны:**
- Красивый, геймифицированный UI (XP, leagues, streaks)
- Привычка через daily reminder
- Stories — контекстные диалоги
- Voice recording с feedback

**Слабые стороны:**
- **Нет SRS** — можно "проходить" уроки бесконечно, забывая старое
- Платная модель (premium lock)
- Нет контекстного интервального повторения
- Нет Telegram

**Наше преимущество:** SRS + Zero-Debt + Telegram

---

### 3.2 Anki — Gold Standard SRS

**Сильные стороны:**
- Лучший SRS-алгоритм (SM-2 + Anki algorithm)
- Open source, гибкость
- Community decks (готовые колоды)
- Полная кастомизация

**Слабые стороны:**
- Ужасный UI (2005 год)
- Нет Telegram
- Нет AI
- Настройка требует времени
- Самостоятельный хостинг

**Наше преимущество:** Telegram + AI generation + Красивый UI

---

### 3.3 Retell (Telegram bot, 12⭐)

**Найден на GitHub:** `usual2970/retell`

**Сильные стороны:**
- Telegram native
- Короткие тексты для чтения +背诵 (заучивание наизусть)
- Голосовая практика
- Контекстные примеры

**Слабые стороны:**
- Нет AI-генерации слов
- Нет SRS (интервалы?)
- Ручной ввод слов
- Нет нескольких уровней (A1-C2)
- Нет gameification
- Нет Zero-Debt

**Наше преимущество:** AI generation + CSRS mechanics + 6-level SRS + CEFR levels

---

### 3.4 VocabMaster (Telegram bot)

**Найден на GitHub:** `CyberSenpa1/english-bot`

**Сильные стороны:**
- Spaced repetition
- Telegram native
- Адаптируется к сложным словам

**Слабые стороны:**
- Нет AI-генерации (слова вручную?)
- Нет смены механики
- Нет CEFR уровней
- Нет gameification
- Open source но без активного развития

**Наше преимущество:** AI generation + CSRS mechanics + Gamification + CEFR

---

### 3.5 FlashCard_ecosystem (AI-powered Italian)

**Найден на GitHub:** `d-khalang/FlashCard_ecosystem`

**Сильные стороны:**
- AI-powered
- Spaced repetition
- Telegram + Web

**Слабые стороны:**
- Итальянский, не английский
- Нет CEFR
- Нет CSRS mechanics
- Мало stars

**Наше преимущество:** English specific + CSRS + CEFR levels

---

## 4. ПОДРОБНЫЙ GAP-АНАЛИЗ НА ОСНОВЕ КОДА

### 4.1 Что уже реализовано (functional inventory)

#### a) SRS System — ✅ Полноценная

```python
SRS_INTERVALS = {
    1: timedelta(hours=4),   # Level 0-1
    2: timedelta(days=1),     # Level 2
    3: timedelta(days=3),     # Level 3
    4: timedelta(days=7),     # Level 4
    5: timedelta(days=14),    # Level 5
    6: timedelta(days=30),   # Level 6 = Learned
}
MAX_BOX_LEVEL = 6
```
**Оценка:** Anki использует похожий SM-2. Это лучше чем Duolingo.

#### b) AI Word Generation — ✅ Работает

```python
# AITutorService.generate_new_vocabulary()
# Gemini: topic + letter entropy = двойная энтропия
# + duplicate check + translation check
```
**Оценка:** Уникально среди Telegram ботов. Retell, VocabMaster делают это вручную.

#### c) CEFR Levels — ✅ Реализовано

```python
# Word model has cefr_level
# AITutor генерирует под уровень
```
**Оценка:** Редкость среди ботов.

#### d) Онбординг + Placement Test — ✅ Есть

```python
# PlacementTestQuestion model
# OnboardingStates: goal → schedule → placement_test
```

#### e) Notification System — ✅ Работает

```python
# NotificationManager: daily_new_words, review_reminder
# APScheduler integration
```

#### f) VocabularyRepo — ✅ Полный набор операций

```python
# add_user_word, get_new_user_words, get_words_for_review
# get_global_word, get_today_acquired_words_count
# get_word_duplicate, update_user_word
```

---

### 4.2 Что НЕ реализовано (gap from docx)

| Gap | Docx требование | Текущий код | Статус |
|-----|----------------|-------------|--------|
| **CSRS Mechanics** | Смена механики (Use Case → MC → Reverse → Audio) | Все слова показываются одинаково | ❌ |
| **Zero Debt Gate** | Блокировка новых слов пока SRS queue > 15-20 | Нет проверки перед `get_new_global_words` | ❌ |
| **Accuracy Throttle** | Динамический лимит по accuracy < 70% → 0 слов | Нет tracking accuracy | ❌ |
| **Production Lock** | Каждые 20 слов — голосовой тест | Нет | ❌ |
| **Consolidation Days** | Каждое 7-е число — только повторение | Нет | ❌ |
| **AI Voice Evaluation** | AITutor.evaluate_voice_production() | Нет endpoint | ❌ |
| **Contextual Dialogs** | AI Tutor ведёт мини-разговор | Нет | ❌ |
| **Streaks** | "7 дней подряд" | Нет | ❌ |
| **Progress Bar** | Визуальный прогресс CEFR | Нет | ❌ |
| **Adaptive Topics** | Учёт interests при генерации | `user.settings["topics"]` — есть, но не используется | 🟡 |

---

### 4.3 Critical Bugs (from ANALYSIS_telegram_ux.md)

| Bug | Файл | Серьёзность | Влияние на UX |
|-----|------|-----------|--------------|
| **O(N²) дублирование слов при ошибке** | `words_learning.py:113` | 🔴 P0 | Память + скорость |
| **Race condition card_counter** | `words_learning.py:78` | 🔴 P0 | Потеря данных |
| **Нет позиции в UI** | `for_words.py` | 🔴 P0 | Юзер не знает где |
| **"Предыдущая" всегда active** | `for_words.py` | 🟡 P1 | Невозможное действие |
| **"Назад" не сохраняет позицию** | `words_learning.py` | 🟡 P1 | Потеря прогресса |
| **"Карточки закончились" без статистики** | `for_words.py` | 🟡 P1 | Потеря контекста |

---

## 5. НАШИ СКРЫТЫЕ ПРЕИМУЩЕСТВА

### 5.1 Архитектурные преимущества

1. **Python + Async SQLAlchemy** — асинхронность для масштаба
2. **Модular service design** — `WordsLearningService`, `AITutorService`, `BroadcasterService` — легко расширять
3. **Gemini AI** — уже интегрирован, не нужно платить за OpenAI
4. **CEFR levels** — уже есть в моделях, используются при генерации
5. **Telegram native** — войс, текст, инлайн-клавиатуры

### 5.2 Продуктовые преимущества (не у конкурентов)

1. **CSRS (Contextual SRS)** — менять механику проверки на каждом уровне SRS
2. **AI Tutor для диалогов** — не просто карточки, а разговорная практика
3. **Zero-Debt Rule** — не даёт юзеру халявить
4. **Accuracy Throttle** — адаптивная скорость обучения
5. **Production Lock** — голосовой барьер перед новыми словами
6. **Consolidation Days** — научный подход к памяти

---

## 6. СТРАТЕГИЧЕСКИЕ РЕКОМЕНДАЦИИ

### 6.1 Immediate Wins (что легко реализовать, но даёт большой эффект)

| # | Что | Почему | Effort |
|---|-----|--------|--------|
| **W1** | Починить P0 баги (дублирование, race condition) | Сейчас приложение может терять данные | 2-3h |
| **W2** | Добавить прогресс-бар "Карточка 3 из 10" | Один из главных UX-фидбеков | 1h |
| **W3** | Деактивировать "Предыдущая" на первой карточке | Простая проверка, большой UX | 30min |
| **W4** | Показать статистику при "Карточки закончились" | "Пройдено: 10, Верно: 8" | 1h |

### 6.2 Killer Feature Implementation (CSRS)

Приоритет — **реализовать смену механики по уровню SRS**:

```python
# Механика по SRS box:
BOX_MECHANICS = {
    1: "use_case",      # Показать предложение с пропуском → юзер угадывает
    2: "multiple_choice", # 4 варианта ответа
    3: "reverse_translation", # RU → выбрать EN
    4: "audio_listen",   # Слушаешь войс → пишешь слово
    5: "voice_production", # Записываешь войс с словом → AI проверяет
    6: "learned"         # Финальное закрепление
}
```

### 6.3 AI Voice Production (D1)

```python
# AITutorService.evaluate_voice_production()
# Использовать:
# 1. Google Cloud Speech-to-Text API (или open-source Whisper)
# 2. Gemini для оценки контекста + грамматики
# 3. feedback_text в стиле BroBot
```

### 6.4 Gamification Priority

**Minimal viable gamification (MVP):**

1. **Streaks** — "🔥 7 дней подряд"
2. **Progress bar** — "До B2 осталось 45 слов"
3. **Lesson complete screen** — статистика + CTA

**Не делать сразу:**
- Leagues (как Duolingo) — сложно, не нужно для MVP
- Бейджи до завершенияstreak system
- Weekly goals dashboard

---

## 7. SWOT-АНАЛИЗ

### 7.1 Strengths (Сильные стороны)

| S | Описание |
|---|---------|
| S1 | AI-генерация слов (Gemini) — конкуренты вручную |
| S2 | 6-уровневая SRS — лучше чем Duolingo |
| S3 | CEFR levels — редкость среди Telegram ботов |
| S4 | Telegram native — войс, текст, inline |
| S5 | Open source + self-hosted |
| S6 | BroBot persona — уникальный tone of voice |

### 7.2 Weaknesses (Слабые стороны)

| W | Описание |
|---|---------|
| W1 | Нет CSRS механики (Killer Feature не реализована) |
| W2 | Нет gamification (streaks, progress) |
| W3 | Critical UX bugs (P0 из ANALYSIS) |
| W4 | Нет AI voice evaluation |
| W5 | NotificationManager создаёт сессии в цикле (performance) |
| W6 | words_supply.py содержит TypeError (`ai_service` как конструктор) |

### 7.3 Opportunities (Возможности)

| O | Описание |
|---|---------|
| O1 | Telegram + AI — ниша практически пустая |
| O2 | CSRS = Killer Feature — нет аналогов |
| O3 | Voice production + AI evaluation = уникально |
| O4 | Zero-Debt rule — Duolingo это не умеет |
| O5 | Контекстные диалоги с AI Tutor — новый формат |
| O6 | Self-hosted → приватность → плюс для пользователей |

### 7.4 Threats (Угрозы)

| T | Описание |
|---|---------|
| T1 | retell/vocabmaster могут скопировать AI-генерацию |
| T2 | Duolingo может добавить Telegram-версию |
| T3 | AI-стоимость (Gemini API costs) |
| T4 | Low engagement → пользователи бросают через неделю |
| T5 | Telegram ToS риски (если бот станет слишком spammy) |

---

## 8. КОНКУРЕНТНОЕ Позиционирование

### 8.1 Positioning Statement

> **LearnableLanguage** — это Telegram-бот для изучения английского языка, который использует AI-генерацию слов и **Контекстное Интервальное Повторение (CSRS)** — смену способа проверки на каждом уровне SRS. В отличие от Duolingo, мы не даём забывать выученное. В отличие от Anki, мы красивые и работаем в Telegram.

### 8.2 Target Audience

| Сегмент | Описание | Боль |
|---------|---------|------|
| **Self-directed learners** | Те, кто хочет учить язык без курсов | "Anki скучный, Duolingo не запоминаю" |
| **Telegram natives** | Уже в Telegram 24/7 | "Не хочу отдельное приложение" |
| **Exam prep** | ЕГЭ, TOEFL, IELTS | "Нужно системно, не карточки вслепую" |
| **Busy professionals** | Нет времени на приложения | "5 минут в день — идеально" |

### 8.3 Go-to-Market

1. **Telegram-native growth** — постим в русскоязычных Telegram-чатах про языки
2. **Content marketing** — ведём Telegram-канал о методике
3. **Open source** — выкладываем на GitHub, привлекаем разработчиков
4. **Partnerships** — школы английского, репетиторы

---

## 9. ROADMAP (детализированный)

### 9.1 Фаза 1: Фундамент ( Sprint 1-2 )

**Цель:** Починить критические баги + внедрить Zero-Debt

```
✅ A1: Починить O(N²) дублирование слов (words_learning.py:113)
✅ A2: Починить race condition card_counter (FSM atomic update)
✅ A3: Добавить прогресс-бар "Карточка 3 из 10"
✅ A4: Деактивировать "Предыдущая" на первой карточке
✅ C1: Zero-Debt Rule (SRS queue gate)
```

**Результат:** Стабильное приложение без потери данных.

---

### 9.2 Фаза 2: CSRS — Killer Feature (Sprint 3-4)

**Цель:** Реализовать смену механики проверки по SRS box

```
✅ B1: Use Case механика (box=1) — показать пример с пропуском
✅ B2: Multiple Choice механика (box=2) — 4 варианта
✅ B3: Reverse Translation (box=3) — RU → EN selection
✅ B4: Audio Listen механика (box=4) — бот посылает войс
✅ B5: Voice Production механика (box=5) — запись + AI evaluation
```

**Результат:** Killer Feature готова. Юзер тренирует слово全方位 (со всех сторон).

---

### 9.3 Фаза 3: AI + Gamification (Sprint 5-6)

**Цель:** Дифференциация + удержание

```
✅ D1: AI Voice Production Checker (Whisper/Gemini)
✅ D2: Contextual Dialogues (AI Tutor chats)
✅ E1: Streaks system (7 дней подряд)
✅ E2: Progress bar уровня (CEFR milestone)
✅ D3: Adaptive topic selection (из user.settings["topics"])
```

**Результат:** AI-оценка голоса + привычка через streaks.

---

### 9.4 Фаза 4: Polish + Scale (Sprint 7-8)

**Цель:** UX конкурентный + инфраструктура

```
✅ F1: Loaders + feedback (loading states)
✅ F2: Сохранение позиции при "Назад"
✅ F3: Lesson complete screen со статистикой
✅ G1: Unit tests для core services
✅ G2: CI/CD (GitHub Actions)
✅ F4: Telegram Mini App (опционально)
✅ G3: Monitoring (prometheus metrics)
```

**Результат:** Продакшн-ready приложение.

---

## 10. ВЫВОДЫ

### 10.1 Главное

1. **Наш бот уже лучше чем 90% Telegram english bots** — AI generation + SRS + CEFR
2. **Но не реализован главный дифференциатор** — CSRS (смена механики по уровню)
3. **Critical bugs нужно починить сразу** — они блокируют нормальный UX
4. **Gamification нужен для retention** — без streaks юзеры бросают через неделю
5. **Zero-Debt = наше главное методическое преимущество** — нет аналогов

### 10.2 Что нужно сделать в первую очередь

```
Priority 1 ( immediately ):
├── Починить P0 bugs (A1, A2, A3)
├── Zero-Debt gate (C1)
└── Прогресс-бар в UI (A3)

Priority 2 ( within 2 weeks ):
├── CSRS mechanics (B1-B5)
├── AI voice evaluation (D1)
└── Streaks (E1)

Priority 3 ( within month ):
├── AI dialogs (D2)
├── Gamification (E2-E5)
└── Consolidation Days (C4)
```

### 10.3 Наш MVP (minimum viable product)

Для запуска v1.0 нужно:
1. ✅ SRS 6 уровней — уже есть
2. ✅ AI word generation — уже есть
3. ✅ CSRS mechanics (B1-B5) — **нужно реализовать**
4. ✅ Zero-Debt gate — **нужно реализовать**
5. ✅ Streaks — **нужно реализовать**
6. ✅ Bug fixes (P0) — **нужно починить**

---

_Документ подготовлен планировщиком_
_Детальный анализ для согласования стратегии_
