from django.contrib.auth import get_user_model
from django.db import models
from utils.models import BaseModel

User = get_user_model()


class Chat(BaseModel):
    is_open = models.BooleanField(default=True)


class ChatMember(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='chats')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='members')


class Message(BaseModel):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='messages')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(blank=True, null=True)
    upload = models.FileField(upload_to='messages/', blank=True, null=True)
