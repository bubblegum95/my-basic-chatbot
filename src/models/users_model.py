import uuid
from tortoise import Model, fields


class Users(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(null=False, min_length=2, max_length=10)
    email = fields.CharField(null=False, min_length=5, max_length=40, unique=True)
    password_hash = fields.CharField(null=False, max_length=300)
    refresh_token = fields.CharField(null=True, max_length=300)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)