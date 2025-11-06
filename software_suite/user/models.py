# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator


class UserManager(BaseUserManager):
    use_in_migrations = True


    def create_user(self, username, password = None, first_name = None, last_name = None,
                    role = "software_engineer", **extra_fields):
        if not username:
            raise ValueError("The username must be set")

        # Normalize username to a consistent form (lowercase)
        username = username.strip().lower()
        extra_fields.setdefault('is_active', True)
        user = self.model(
            username=username,
            first_name=first_name or "",
            last_name=last_name or "",
            role=role,
            **extra_fields
        )
        if password:
            user.set_password(password)
        else:
            # If you want to enforce that normal user must set a password:
            raise ValueError("User must have a password.")
        user.save(using=self._db)
        return user


    def create_superuser(self, username, password = None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if not password:
            raise ValueError("Superuser must have a password.")

        # You can force an admin role for superusers if you like:
        return self.create_user(username, password, role="admin", **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("product_manager", "Product Manager"),
        ("admin", "Admin"),
        ("software_engineer", "Software Engineer"),
        ("software_architect", "Software Architect"),
        ("data_engineer", "Data Engineer"),
    ]

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(unique=True, max_length=30, validators=[username_validator])
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="software_engineer")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []


    def __str__(self):
        return self.username
