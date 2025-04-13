"""Engine redis"""
from redis.asyncio import Redis

from ..utils.config import settings

redis = Redis(host=settings.DB_HOST, port=6379, password=settings.DB_PASSWORD)