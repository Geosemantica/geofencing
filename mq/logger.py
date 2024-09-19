import logging

__all__ = ['consumer_logger',
           'publisher_logger']

FORMAT = '%(asctime)s-%(name)s | %(levelname)s  %(message)s'
logging.basicConfig(format=FORMAT, level='INFO')

consumer_logger = logging.getLogger('mq_consumer')
publisher_logger = logging.getLogger('mq_publisher')
