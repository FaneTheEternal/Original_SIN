import logging

logger = logging.getLogger(__name__)

try:
    logger.info(f'telebot_seller startup...')
    # from . import telebot_seller
    logger.info('Success')
except Exception as e:
    import traceback

    logger.error(f'Cant init telebot_seller cause: {e}')
    logger.error(traceback.format_exc())
