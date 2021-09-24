import datetime
import logging
from collections import defaultdict
from pathlib import Path

import vk_api
from django.conf import settings
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        token = getattr(settings, 'CHUVSU_VK_TOKEN')
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()

        msgs = defaultdict(list)  # peer: messages

        st = datetime.datetime(2021, 6, 1)
        et = datetime.datetime(2021, 9, 1)

        conversation_offset = 0
        while True:
            logger.info(f'getConversations with offset={conversation_offset}')
            response = vk.messages.getConversations(offset=conversation_offset)
            conversations = []
            # Получаем диалоги
            if response['items']:
                conversation_offset += len(response["items"])
                # logger.info(f'Get {response["count"]} conversations')
                # logger.info(f'Real {len(response["items"])} conversations')
                conversations = response['items']
            else:
                # logger.warning('Empty query')
                break

            # Обрабатываем сообщения
            for conversation in conversations:
                peer = conversation['conversation']['peer']
                peer_id = peer['id']
                offset = 0
                # logger.info(f'Start msgs with {peer_id}')
                awhile = True
                while awhile:
                    response = vk.messages.getHistory(
                        offset=offset,
                        peer_id=peer_id,
                        rev=0,
                    )
                    if response['items']:
                        offset += len(response['items'])
                        for item in response['items']:
                            text = item['text']
                            date = datetime.datetime.fromtimestamp(item['date'])
                            if text == 'Поступающим':
                                if st <= date < et:
                                    msgs[peer_id].append(item)
                            if date < st:
                                awhile = False
                                break
                    else:
                        # logger.warning('Empty query messages')
                        break

                count = len(msgs.get(peer_id, []))
                if count:
                    logger.info(f'Find {count} entries with {peer_id}')
        logger.info(f'Find {len(msgs.keys())} user entries')
        val = 0
        for i in msgs.values():
            val += len(i)
        logger.info(f'Total {val} entries')
        path = Path(getattr(settings, 'BASE_DIR')).joinpath('send_stats_repr.txt')
        open(path, 'w').write(repr(msgs))
