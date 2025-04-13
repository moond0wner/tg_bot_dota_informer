__all__ = ("router", )

from aiogram import Router
from .user.private import router as private_user_router
from .user.group.handlers import router as group_user_router

router = Router()
router.include_routers(private_user_router, group_user_router)