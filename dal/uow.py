from typing import Optional

from sqlalchemy.ext.asyncio.session import async_sessionmaker, AsyncSession

from dal.db import session_factory
from dal.repository.base import Repository
from dal.repository.expl_repo import ExplosionAreaRepository
from dal.repository.metadata_repo import MetadataRepository
from dal.repository.mining_repo import MiningAreaRepository
from dal.repository.outbox import OutboxRepository
from dal.repository.proj_repo import ReprojectRuleRepository


class PostgisUow:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], repositories: list[Repository]):
        self.session_factory = session_factory
        self._session: Optional[AsyncSession] = None
        self.__repositories: dict[str, Repository] = {repository.__rname__: repository for repository in repositories}

    async def commit(self):
        if not self._session:
            raise RuntimeError('No session was initialized')
        await self._session.commit()

    async def refresh(self, model):
        await self._session.refresh(model)

    def __getattr__(self, repo_name: str):
        return self.__repositories.get(repo_name)

    async def __aenter__(self):
        self._session = self.session_factory()
        self._set_up_session()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self._session.rollback()
        self._rm_session()
        await self._session.close()
        self._session = None

    def _set_up_session(self):
        for repo in self.__repositories.values():
            repo.session = self._session

    def _rm_session(self):
        for repo in self.__repositories.values():
            repo.session = None


def get_uow() -> PostgisUow:
    return PostgisUow(session_factory, [ExplosionAreaRepository(),
                                        ReprojectRuleRepository(),
                                        MiningAreaRepository(),
                                        OutboxRepository(),
                                        MetadataRepository()])
