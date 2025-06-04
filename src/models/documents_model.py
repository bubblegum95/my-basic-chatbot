from tortoise import Model, fields
import uuid
from src.models.collections_model import Collections


class Documents(Model):
  id = fields.UUIDField(pk=True, default=uuid.uuid4)
  path = fields.TextField()
  created_at = fields.DatetimeField(auto_now_add=True)
  collection = fields.ForeignKeyField(model_name="models.Collections", related_name="documents", null=False)