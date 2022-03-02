import os
import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create(self, email, username, is_superuser, created_by, updated_by, password=None):
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            is_superuser=is_superuser,
            is_notifiable=is_notifiable,
            created_by=created_by,
            updated_by=updated_by
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


# This model represents the user.
class Quarreler(AbstractBaseUser):
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=30, unique=True)
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=50)
    updated_by = models.CharField(max_length=50)

    def __str(self):
        return str(self.email)


class Game(models.Model):
    primary_user = models.ForeignKey(Quarreler, related_name='primary_user', on_delete=models.CASCADE, null=True)
    secondary_user = models.ForeignKey(Quarreler, related_name='secondary_user', on_delete=models.CASCADE, null=True)
    answer = models.CharField(max_length=30, null=True)
    guess1 = models.CharField(max_length=30, null=True)
    guess2 = models.CharField(max_length=30, null=True)
    guess3 = models.CharField(max_length=30, null=True)
    guess4 = models.CharField(max_length=30, null=True)
    guess5 = models.CharField(max_length=30, null=True)
    guess6 = models.CharField(max_length=30, null=True)
    # solution_time = models.PositiveIntegerField()
    correct_guess = models.PositiveIntegerField(null=True)
    primary_elo = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    secondary_elo = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    elo_change = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    game_id = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    is_ranked = models.BooleanField(default=False)
    primary_guest = models.CharField(max_length=40)
    secondary_guest = models.CharField(max_length=40, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=50)
    updated_by = models.CharField(max_length=50)

    def __str__(self):
        return str(self.game_id) + str(self.primary_user) + str(self.secondary_user) + str(self.guess1) + str(self.guess2) + str(self.guess3) + str(self.guess4) + str(self.guess5) + str(self.guess6)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    frontend_url = os.environ['QUARREL_FRONTEND_URL']
    # frontend_url = "a"
    message = "Hello, please click the link below to reset your password: "
    email_plaintext_message = message + frontend_url + "{}?token={}".format(
        reverse('password_reset:reset-password-request'), reset_password_token.key)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="Quarrel"),
        # message:
        email_plaintext_message,
        # from:
        "quarrelgame@gmail.com",
        # to:
        [reset_password_token.user.email]
    )
