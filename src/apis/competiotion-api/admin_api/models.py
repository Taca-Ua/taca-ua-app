"""
Django models for admin_api app
"""

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Manager for User model"""

    def create_user(self, username, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault("role", "geral")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model for administrators (nucleo and geral)
    """

    class Role(models.TextChoices):
        NUCLEO = "nucleo", "Núcleo"
        GERAL = "geral", "Geral"

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.NUCLEO)
    course_id = models.IntegerField(null=True, blank=True)
    course_abbreviation = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.username} ({self.role})"

    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check password"""
        from django.contrib.auth.hashers import check_password

        return check_password(raw_password, self.password)
