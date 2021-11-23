from django.db.models.deletion import CASCADE
from user.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

import uuid

# ID Generation
def unique_id():
    return uuid.uuid4().hex[:8].lower()

class Chat(models.Model):
    chat_id = models.CharField(primary_key=False, default=unique_id, max_length=10, editable=False, unique=True)
    name = models.CharField(max_length=40)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=CASCADE, null=True)
    location = models.PointField(geography=True, default=Point(0,0))
    radius = models.FloatField(default=5)
    polygon = models.PolygonField(geography=True, null=True)
    password = models.CharField(max_length=50, null=True)
    image = models.ImageField(null=True)

    def save(self, *args, **kwargs):
        while Chat.objects.filter(chat_id=self.chat_id).exists() and self.pk is None and DirectChat.objects.filter(chat_id=self.chat_id):
            self.chat_id = unique_id()
        super(Chat, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class DirectChat(models.Model):
    chat_id = models.CharField(primary_key=False, default=unique_id, max_length=10, editable=False, unique=True)
    user1 = models.ForeignKey(User, on_delete=CASCADE, null=True, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=CASCADE, null=True, related_name='user2')

    def save(self, *args, **kwargs):
        while Chat.objects.filter(chat_id=self.chat_id).exists() and self.pk is None and DirectChat.objects.filter(chat_id=self.chat_id).exists():
            self.chat_id = unique_id()
        super(DirectChat, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.user1.username + " " + self.user2.username

class MemberOf(models.Model):
    chat = models.ForeignKey(Chat, on_delete=CASCADE)
    user = models.ForeignKey(User, on_delete=CASCADE)

    def __str__(self):
        return self.user.username + " " + self.chat.name

class Message(models.Model):
    message_id = models.CharField(primary_key=False, default=unique_id, max_length=10, editable=False, unique=True)
    chat = models.ForeignKey(Chat, on_delete=CASCADE)
    sender = models.ForeignKey(User, on_delete=CASCADE)
    content = models.TextField()
    file = models.FileField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        while Message.objects.filter(message_id=self.message_id).exists() and self.pk is None and DirectMessage.objects.filter(message_id=self.message_id):
            self.message_id = unique_id()
        super(Message, self).save(*args, **kwargs)

class DirectMessage(models.Model):
    message_id = models.CharField(primary_key=False, default=unique_id, max_length=10, editable=False, unique=True)
    chat = models.ForeignKey(DirectChat, on_delete=CASCADE)
    sender = models.ForeignKey(User, on_delete=CASCADE, related_name='sender')
    content = models.TextField()
    file = models.FileField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        while Message.objects.filter(message_id=self.message_id).exists() and self.pk is None and DirectMessage.objects.filter(message_id=self.message_id):
            self.message_id = unique_id()
        super(DirectMessage, self).save(*args, **kwargs)

class MessageLike(models.Model):
    message = models.ForeignKey(Message, on_delete=CASCADE)
    user = models.ForeignKey(User, on_delete=CASCADE)
    class Meta:
        unique_together = ('message', 'user',)

class DirectMessageLike(models.Model):
    message = models.ForeignKey(DirectMessage, on_delete=CASCADE)
    user = models.ForeignKey(User, on_delete=CASCADE)
    class Meta:
        unique_together = ('message', 'user',)
