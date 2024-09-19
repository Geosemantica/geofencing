from datetime import datetime, timezone

from dal.models import Metadata
from dal.uow import *
from mq.publisher import MqPublisher, get_mq_publisher, get_mq_settings


async def publish_outbox(batch_size: int = 100):
    uow: PostgisUow = get_uow()
    metadata_repo: MetadataRepository = uow.metadata
    outbox_repo: OutboxRepository = uow.outbox
    publisher: MqPublisher = await get_mq_publisher()

    current_time = datetime.now(timezone.utc)
    offset = 0
    async with uow:
        metadata = await metadata_repo.get()
        while True:
            messages = await outbox_repo.get_from_dt_interval(metadata.processed_at if metadata else None,
                                                              current_time, batch_size, offset)
            if not messages:
                break
            for message in messages:
                await publisher.publish(message.body, get_mq_settings().fencing_indicators_ex)
            offset += batch_size
        await outbox_repo.delete_before_dt(current_time)

        if not metadata:
            metadata = Metadata()
        metadata.processed_at = current_time
        await metadata_repo.save(metadata)

        await uow.commit()
