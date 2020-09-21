from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import vk_api
from vk_api.exceptions import ApiError

from .bot_config import token, secret_key, confirmation_token
from . import chat_bot
from .models import VkUser

import json
import sys


@csrf_exempt
def index(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if data['secret'] == secret_key:
            if data['type'] == 'confirmation':
                """
                For confirmation my server (webhook) it must return
                confirmation token, whitch issuing in administration web-panel
                your public group in vk.com.

                Using <content_type="text/plain"> in HttpResponse function allows you
                response only plain text, without any format symbols.
                Parametr <status=200> response to VK server as VK want.
                """
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
                return HttpResponse(
                    'ok',
                    content_type="text/plain",
                    status=200
                    )
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
                        user, _ = VkUser.objects.using('old_bot').get_or_create(user_id=peer_id)
                        chat_bot.go_home(vk, user)
            return HttpResponse(
                    'ok',
                    content_type="text/plain",
                    status=200
                    )
    else:
        return HttpResponse('see you :)')


@csrf_exempt
def fill(request):
    response = 'got ' + request.method
    if request.method == 'POST':
        try:
            data = request.POST.copy()
            data = dict(data)
            data = data.get('data')
            data = data[0]
            data = data.split()
            data = ((i.split(':')) for i in data)
            data = dict(data)
            bulk = []
            for user_id, status in data.items():
                obj = VkUser(user_id=user_id, status=status)
                bulk.append(obj)
            VkUser.objects.using('old_bot').bulk_create(bulk, batch_size=100)
        except Exception as e:
            response += f' {e}'
        else:
            response += ' <created>'
    return HttpResponse(response)


def raw(request):
    qs = VkUser.objects.using('old_bot').all()
    ids = ['{id}:{status}'.format(id=i.user_id, status=i.status) for i in qs]
    result = ' '.join(ids)
    return HttpResponse(result)
