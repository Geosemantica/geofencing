from typing import Final

from sqlalchemy.ext.asyncio.engine import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from dal.settings import get_db_settings

engine: Final[AsyncEngine] = create_async_engine(get_db_settings().dsn, echo=True)
session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, autocommit=False)
