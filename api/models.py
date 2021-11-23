from django.db.models.deletion import CASCADE
from user.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

import uuid

# ID Generation
def unique_id():
    return uuid.uuid4().hex[:8].lower()

# class EventType(models.Model):
#     SELECT = 'S'
#     GA= 'GA'
#     GA_SECTION = 'GAS'
#     EVENT_TYPES = [
#         (SELECT, 'Select Seats'),
#         (GA, 'General Admission'),
#         (GA_SECTION, 'GA with Section Select'),
#     ]
#     school = models.ForeignKey(School, on_delete=CASCADE)
#     sport = models.ForeignKey(Sport, on_delete=CASCADE)
#     event_type = models.CharField(max_length=3, choices=EVENT_TYPES, default=SELECT)
#     thumbnail = models.URLField(max_length=200, blank=True, null=True)
#     header = models.URLField(max_length=200, blank=True, null=True)
    
#     def __str__(self):
#         return self.school.name + " " + self.sport.name

class Chat(models.Model):
    chat_id = models.CharField(primary_key=False, default=unique_id, max_length=10, editable=False, unique=True)
    name = models.CharField(max_length=40)
    desciption = models.TextField()
    owner = models.ForeignKey(User, on_delete=CASCADE, null=True)
    location = models.PointField(geography=True)
    radius = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        while Chat.objects.filter(team_id=self.team_id).exists() and self.pk is None:
            self.team_id = unique_id()
        super(Chat, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name
