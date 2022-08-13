from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import  AsyncSession, create_async_engine
from library.config import config

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