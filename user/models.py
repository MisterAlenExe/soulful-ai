from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if email is None:
            raise TypeError("Email is required")
        if password is None:
            raise TypeError("Password is required")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):
        if password is None:
            raise TypeError("Password is required")

        return self.create_user(
            email=email,
            password=password,
            is_superuser=True,
            is_staff=True,
        )


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="Email",
        max_length=50,
        blank=True,
        unique=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self):
        return self.email
