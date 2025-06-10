import uuid
from tortoise import Model, fields


class Collections(Model):
  id = fields.UUIDField(pk=True, default=uuid.uuid4)
  user = fields.ForeignKeyField(model_name="models.Users", related_name="collections", null=False)
  name = fields.CharField(min_length=2, max_length=100, null=False)
  topic = fields.CharField(min_length=2, max_length=100, null=False)
  created_at = fields.DatetimeField(auto_now_add=True)
  updated_at = fields.DatetimeField(auto_now=True)