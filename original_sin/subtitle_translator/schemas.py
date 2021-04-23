from typing import List
from uuid import UUID

from ninja import Schema, File, UploadedFile


class TryLoginSchema(Schema):
    uid: str = None


class LoginSchema(Schema):
    uid: str


class FileSchema(LoginSchema):
    hash: str
    file_name: str


class ParserSchema(LoginSchema):
    parser: str


class TranslatorsSchema(LoginSchema):
    translators: List[str]


class TranslatorParamsSchema(LoginSchema):
    src: str
    dest: str
