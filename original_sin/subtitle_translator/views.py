import logging
import sys
from hashlib import sha256
import traceback
import os
import json
from uuid import UUID

from django.core.files.base import ContentFile
from django.http import FileResponse, HttpResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from ninja import NinjaAPI, UploadedFile, File

from core.utility import get_filename
from subtitle_translator.logic import prepare_env, save_changes
from subtitle_translator.models import SimpleUser, NameLessFile
from subtitle_translator.schemas import LoginSchema, FileSchema, TryLoginSchema, ParserSchema, TranslatorsSchema, \
    TranslatorParamsSchema
from subtitle_translator.tasks import translate_invoke
from subtitle_translator.utility import allowed_subtitles, allowed_translations, get_parser

api = NinjaAPI()

logger = logging.getLogger(__name__)


# Info views
@api.get('/allowed_types')
def allowed_types(request):
    return {'types': allowed_subtitles()}


@api.get('/allowed_translations')
def allowed_translators(request):
    return {'types': allowed_translations()}


# Logic views
@api.post('/login')
def login_view(request, login: TryLoginSchema):
    uid = login.uid
    if uid:
        user, created = SimpleUser.objects.get_or_create(uid=UUID(uid))
    else:
        user = SimpleUser.objects.create()
        created = True
    response = dict(
        created=created,
        uid=str(user.uid),
    )
    if not created:
        if user.file:
            response['file'] = os.path.basename(user.file.name)
        if user.file and user.translators_cache:
            response['cache'] = user.translators_cache
        if user.file_result:
            response['file_result'] = os.path.basename(user.file_result.name)
        response['parser'] = user.parser
        response['translators'] = user.translators
        response['translators_params'] = user.translators_params
    return response


@api.post('/upload')
def upload_nameless(request, file: UploadedFile = File(...)):
    try:
        assert file, 'None of file'
        file_sha = sha256(file.read()).hexdigest()
        NameLessFile.objects.update_or_create(
            dict(hash=file_sha, file=file),
            hash=file_sha,
        )
        return {
            'result': 'ok',
            'hash': file_sha,
        }
    except Exception:
        import traceback
        # print(traceback.format_exc())
    return {'result': 'error'}


@api.post('/prepare_file')
def prepare_file(request, file: FileSchema):
    uid = file.uid
    file_sha = file.hash
    file_name = file.file_name
    try:
        file = NameLessFile.objects.get(hash=file_sha)
        user, _ = prepare_env(uid, load_parser=False)
        user.file.save(file_name, file.file)
        save_changes(user)
        file.file.delete()
        file.delete()
        return {
            'result': 'ok',
            'got': os.path.basename(user.file.name),
        }
    except Exception as e:
        traceback.print_exc()
        return {
            'result': 'error',
            'error': str(e)
        }


@api.post('/set_translators')
def set_translators(request, obj: TranslatorsSchema):
    uid = obj.uid
    translators = obj.translators
    try:
        user, _ = prepare_env(uid, load_parser=False)
        user.translators = translators
        save_changes(user)
        return {'result': 'ok'}
    except Exception as e:
        return {
            'result': 'error',
            'error': str(e)
        }


@api.post('/set_translators_params')
def set_translators_params(request, obj: TranslatorParamsSchema):
    uid = obj.uid
    src = obj.src
    dest = obj.dest
    try:
        user, parser = prepare_env(uid, load_parser=False)
        user.translators_params = dict(
            src=src,
            dest=dest,
            force=False,
        )
        save_changes(user, parser)
        return {'result': 'ok'}
    except Exception as e:
        return {
            'result': 'error',
            'error': str(e)
        }


@api.post('/choice_parser')
def choice_parser(request, obj: ParserSchema):
    uid = obj.uid
    parser = obj.parser
    try:
        user, _ = prepare_env(uid, load_parser=False)
        user.parser = parser
        save_changes(user)
        return {'result': 'ok'}
    except Exception as e:
        return {
            'result': 'error',
            'error': str(e)
        }


@api.post('/invoke')
def invoke(request, obj: LoginSchema):
    uid = obj.uid
    try:
        user, parser = prepare_env(uid)
        translate_invoke(user, parser)
        return {'result': 'ok'}
    except Exception as e:
        import traceback
        # print(traceback.format_exc())
        return {
            'result': 'error',
            'error': str(e),
            'traceback': traceback.format_exc(),
        }


@api.post('/check')
def check(request, obj: LoginSchema):
    uid = obj.uid
    try:
        user, parser = prepare_env(uid)
        return {'result': 'ok', 'status': user.translators_cache is not None}
    except Exception as e:
        return {
            'result': 'error',
            'error': str(e)
        }


@api.post('/replace')
def replace(request, uid: str, index: int, s: str):
    try:
        user, parser = prepare_env(uid)
        parser.replace(index, s)
        save_changes(user, parser)
        return {'result': 'ok'}
    except Exception as e:
        return {
            'result': 'error',
            'error': str(e)
        }


@api.post('/result')
def get_result(request, obj: LoginSchema):
    """ Generate & return result file url """
    uid = obj.uid
    try:
        user, parser = prepare_env(uid)
        data = parser.build()
        prefix = f'[{now()}]'
        file_name = prefix + get_filename(user.file.name)
        user.file_result.save(file_name, ContentFile(data))
        save_changes(user, parser)
        return {'result': 'ok', 'file': file_name}
    except Exception as e:
        import traceback
        return {
            'result': 'error',
            'error': str(e),
            'traceback': traceback.format_exc(),
        }


@csrf_exempt
def download_view(request, *args, **kwargs):
    if request.method == "POST":
        data = json.loads(request.body)
        uid = data['uid']
        user, _ = prepare_env(uid, load_parser=False)
        response = FileResponse(user.file_result.open())
        return response
    return HttpResponse('qq')
