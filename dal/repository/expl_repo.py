from dal.models import ExplosionArea
from dal.repository.base import Repository


class ExplosionAreaRepository(Repository):
    __rname__ = 'explosion'

    async def save(self, model: ExplosionArea):
        self.session.add(model)
        await self.session.flush([model])
        await self.session.refresh(model)

        return model
