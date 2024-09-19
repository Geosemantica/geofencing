from sqlalchemy import select

from dal.models import Metadata
from dal.repository.base import Repository


class MetadataRepository(Repository):
    __rname__ = 'metadata'

    async def save(self, model: Metadata) -> Metadata:
        self.session.add(model)
        await self.session.flush([model])
        await self.session.refresh(model)

        return model

    async def get(self) -> Metadata:
        return (await self.session.execute(select(Metadata))).scalar()
