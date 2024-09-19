import logging
from types import MappingProxyType
from typing import Final, Callable, Type, Awaitable

from dal.events import *
from dal.models import *
from dal.uow import PostgisUow

__all__ = [
    'handle'
]


async def handle(event: Event, uow: PostgisUow):
    for handler in HANDLERS.get(type(event), []):
        await handler(event, uow)


async def add_area_to_outbox(event: MiningAreaEvent | ExplosionAreaEvent, uow: PostgisUow):
    model = Outbox(
        message_id=event.message_id,
        type=event.type,
        body=event.model_dump_json(by_alias=True)
    )
    await uow.outbox.save(model)
    logging.info(f'Saved event to outbox: {event}')


HANDLERS: Final[MappingProxyType[Type[Event], list[Callable[..., Awaitable]]]] = MappingProxyType({
    MiningAreaEvent: [add_area_to_outbox],
    ExplosionAreaEvent: [add_area_to_outbox]
})
