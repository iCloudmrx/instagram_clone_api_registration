from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from users.models import User
from shared.models import BaseModel

# Create your models here.
class ChatRoom(BaseModel):
    sender = models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    receiver = models.ForeignKey(User, models.CASCADE, null=True, blank=True, related_name='receivers')
    message = models.TextField(validators=[
        MinLengthValidator(1),
        MaxLengthValidator(4000)
    ])

    def __str__(self):
        return self.message