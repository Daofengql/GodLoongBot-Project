from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from library.config import config


class redis_db_pool(object):
    def __init__(self) -> None:
        pass

    async def get_redis_session(self) ->aioredis.Redis:
    
        redis:aioredis.Redis = await aioredis.from_url(config.redis)
        

        return redis

class mysql_db_pool(object):
    def __init__(self) -> None:
        self.engine1 = create_async_engine(config.db.link, pool_pre_ping=True, pool_use_lifo=True, pool_recycle=3600, max_overflow=1000, pool_size=5000)
        self.Database_Read = sessionmaker(
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            bind=self.engine1
        )
        
    async def get_db_session(self) -> sessionmaker:
        return self.Database_Read