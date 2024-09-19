from datetime import datetime
from typing import Sequence

from sqlalchemy import select, delete, func

from dal.models import Outbox
from dal.repository.base import Repository


class OutboxRepository(Repository):
    __rname__ = 'outbox'

    async def save(self, model: Outbox) -> Outbox:
        self.session.add(model)
        await self.session.flush([model])
        await self.session.refresh(model)

        return model

    async def get_from_dt_interval(self, dt_1: datetime, dt_2: datetime, limit=None, offset=0) -> Sequence[Outbox]:
        stmt = select(Outbox).where(Outbox.created_at.op('<@')(func.tstzrange(dt_1, dt_2, '[)'))) \
            .order_by(Outbox.created_at).offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        return (await self.session.scalars(stmt)).all()

    async def delete_before_dt(self, dt: datetime):
        stmt = delete(Outbox).where(Outbox.created_at < dt)

        await self.session.execute(stmt)
