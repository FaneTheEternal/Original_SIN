from ninja import Schema


class TryLoginSchema(Schema):
    uid: str = None


class LoginSchema(Schema):
    uid: str


class BookSchema(Schema):
    uid: str
