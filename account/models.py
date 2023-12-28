from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from uuid import uuid4
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError()
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    subscription_id = models.CharField(max_length=127, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=127, blank=True, null=True)
    subscription_due = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    objects = UserManager()

    def is_subscribed(self):
        return timezone.now() < self.subscription_due

class PaymentSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email+str(self.created_at)