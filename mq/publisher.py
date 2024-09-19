from aio_pika import connect_robust, Message, DeliveryMode
from aio_pika.exceptions import DeliveryError, ChannelClosed
from aiormq.abc import Basic
from async_lru import alru_cache

from mq.logger import publisher_logger as logger
from mq.settings import MqSettings, get_mq_settings


class MqPublisher:
    def __init__(self, config: MqSettings):
        self.config = config
        self._channel = None

    async def connect(self):
        try:
            conn = await connect_robust(self.config.dsn)
            logger.info('Connected to server...')

            self._channel = await conn.channel()
            logger.info('Open channel...')
        except Exception as e:
            logger.error(f'Cannot connect to rabbitmq server: {str(e)}')
            raise

    async def publish(self, message: str, exchange: str, rk: str = '*') -> bool:
        if not self._channel:
            raise RuntimeError('Use connect method firstly')
        exchange = await self._channel.get_exchange(exchange, ensure=False)
        retries = self.config.publisher_retry_attempts
        while retries:
            try:
                confirmation = await exchange.publish(
                    Message(message.encode('utf-8'), delivery_mode=DeliveryMode.PERSISTENT),
                    routing_key=rk
                )
            except DeliveryError as e:
                logger.error(f'No confirmation was accepted for message: {message}, retry')
                retries -= 1
                continue
            except ChannelClosed as e:
                logger.error(f'Exchange not found: {str(e)}')
                break
            else:
                if not isinstance(confirmation, Basic.Ack):
                    logger.error(f"Message {message} was not acknowledged by broker, retry")
                    retries -= 1
                    continue
                logger.info(f'Published message {message} to exc {exchange} with key {rk}')
                return True
        return False


@alru_cache
async def get_mq_publisher() -> MqPublisher:
    publisher = MqPublisher(get_mq_settings())
    await publisher.connect()

    return publisher
