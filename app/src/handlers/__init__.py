__all__ = ("router", )

from aiogram import Router
from .user.private import router as private_user_router


router = Router()
router.include_router(private_user_router)