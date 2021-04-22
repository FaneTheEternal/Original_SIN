from typing import List

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import vk_api
from vk_api.exceptions import ApiError

from . import chat_bot
from .models import VkUser, QuestProfile, IncomingProfile

import json
import sys


@csrf_exempt
def index(request):
    token = getattr(settings, 'CHUVSU_VK_TOKEN')
    secret_key = getattr(settings, 'CHUVSU_VK_SECRET_KEY')
    confirmation_token = getattr(settings, 'CHUVSU_VK_CONFIRMATION_TOKEN')

    if request.method == "POST":
        data = json.loads(request.body)
        if data['secret'] == secret_key:
            if data['type'] == 'confirmation':
                return HttpResponse(
                    confirmation_token,
                    content_type="text/plain",
                    status=200
                )
            if data['type'] == 'message_new':
                try:
                    chat_bot.execute(data)
                except Exception as e:
                    print(e, file=sys.stderr)
            if data['type'] == 'message_reply':
                vk_session = vk_api.VkApi(token=token)
                vk = vk_session.get_api()
                obj = data['object']
                text = obj['text']
                if text == '!Начать':
                    message_ids = obj['id']
                    spam = int(False)
                    group_id = data['group_id']
                    delete_for_all = int(True)
                    peer_id = obj['peer_id']
                    try:
                        vk.messages.delete(
                            message_ids=message_ids,
                            spam=spam,
                            group_id=group_id,
                            delete_for_all=delete_for_all,
                        )
                    except ApiError as pezdos:
                        print('message_ids: ', message_ids, file=sys.stderr)
                        print('group_id: ', group_id, file=sys.stderr)
                        print('delete_for_all: ', delete_for_all, file=sys.stderr)
                        print('Pezdos: ', pezdos, file=sys.stderr)
                    else:
                        user, _ = VkUser.objects.get_or_create(user_id=peer_id)
                        chat_bot.go_home(vk, user)
            return HttpResponse(
                'ok',
                content_type="text/plain",
                status=200
            )
        else:
            return HttpResponse(
                'Invalid secret'
            )
    return HttpResponse('see you :)')


@csrf_exempt
def fill(request):
    user = getattr(request, 'user')
    try:
        assert user.is_superuser, 'You must be a superuser'
        assert request.method == 'POST', 'Except POST'
        data = json.loads(request.body)
        counter = 0
        for row in data:
            obj = dict(
                user_id=row['user_id'],
                status=row['status'],
            )
            user, created = VkUser.objects.update_or_create(obj, user_id=row['user_id'])
            if row['quest_profile']:
                quest, _ = QuestProfile.objects.update_or_create(
                    dict(user=user, data=row['quest_profile']), user=user)
            if row['incoming_profile']:
                incoming, _ = IncomingProfile.objects.update_or_create(
                    dict(user=user, status=row['incoming_profile']), user=user)
            counter += 1
        return HttpResponse(f'Affected {counter} users')
    except Exception as e:
        return HttpResponse(f'Error cause: {e}: {getattr(e, "message", "hz")}')


def raw(request: WSGIRequest):
    user = getattr(request, 'user')
    try:
        assert user.is_superuser, 'You must be a superuser'
        users: List[VkUser] = VkUser.objects.all().prefetch_related('quest_profile', 'incoming_profile')
        data = [{
            'user_id': user.user_id,
            'status': user.status,
            'quest_profile': user.get_quest_data(),
            'incoming_profile': user.get_incoming_data(),
        } for user in users]
        response = json.dumps(data)
        return HttpResponse(response)
    except Exception as e:
        return HttpResponse(f'Error cause: {e}: {getattr(e, "message", "hz")}')
