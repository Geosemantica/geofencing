from typing import Protocol, Optional

from sqlalchemy.ext.asyncio.session import AsyncSession


class Repository(Protocol):
    __rname__ = 'repository'

    def __init__(self, session=None):
        self.session: Optional[AsyncSession] = session
