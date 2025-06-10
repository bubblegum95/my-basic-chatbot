from tortoise import Model, fields
import uuid


class ChatHistory(Model):
  id = fields.UUIDField(pk=True, default=uuid.uuid4)
  user_message = fields.TextField()
  chat_response = fields.TextField()
  created_at = fields.DatetimeField(auto_now_add=True)
  collection = fields.ForeignKeyField(model_name="models.Collections", related_name="chathistory")