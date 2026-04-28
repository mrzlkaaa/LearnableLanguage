from aiogram import Router, Dispatcher

from .user_main import router as user_router
from .user.onboarding import router as onboarding_router
from .user.words_learning import router as words_router
from .base_navigation import router as general_router
from .notifications import router as notification_router
# from .admin import admin_router
# from .fce import fce_router  (добавим позже)
# from .voice import voice_router (добавим позже)

def setup_routers() -> Router:
    """
    Собирает корневой роутер приложения.
    Порядок регистрации ВАЖЕН! (Сначала специфичные, потом общие)
    """
    root_router = Router(name="root_router")
    
    # Сначала админка (у нее жесткие фильтры)
    # root_router.include_router(admin_router)
    
    # Потом FCE и Voice (добавим позже)
    
    # В конце - общие юзерские хендлеры (типа 'echo' или 'start')
    root_router.include_routers(
        user_router,
        onboarding_router,
        words_router,
        general_router,
        notification_router,
    )
    
    return root_router