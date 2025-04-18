__all__ = ("router", )

from aiogram import Router
from .user.private import router as private_user_router
from .admin.admin_panel import router as admin_router


router = Router()
router.include_routers(private_user_router, admin_router)