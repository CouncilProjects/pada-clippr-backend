from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # AbstractUser already includes: username, email, password, first_name, last_name
    phone = models.CharField(max_length=20, blank=True)
    is_verified_seller = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def get_role_name(self):
        if not self.is_authenticated:
            return 'ANONYMOUS'
        if self.is_staff or self.is_superuser:
            return 'ADMIN'
        if self.is_verified_seller:
            return 'SELLER'
        return 'MEMBER'
