from uuid import UUID

from dal.models import ReprojectRule
from dal.repository.base import Repository


class ReprojectRuleRepository(Repository):
    __rname__ = 'reproject'

    async def get_by_id(self, r_id: UUID):
        return await self.session.get(ReprojectRule, r_id)
