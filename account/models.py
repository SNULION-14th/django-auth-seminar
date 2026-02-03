# ./account/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    college = models.CharField(max_length=32, blank=True)
    major = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return f"id={self.id}, username={self.username}, college={self.college}, major={self.major}"