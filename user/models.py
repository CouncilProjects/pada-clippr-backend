from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # AbstractUser already includes: username, email, password, first_name, last_name
    is_seller = models.BooleanField(default=False)
    phone=models.CharField(max_length=20, blank=True)

    #for seller
    is_verified_seller= models.BooleanField(default=False)

    #for buyer


    def __str__(self):
        return self.username  