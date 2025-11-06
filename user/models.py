# users/models.py
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import EmailValidator
from django.utils import timezone


def avatar_upload_path(instance, filename):
    """
    Generate upload path for user avatar.
    Format: avatars/user_{user_id}/avatar_{user_id}.{ext}
    """
    ext = filename.split('.')[-1]
    # Use user ID if available, otherwise use 'temp' for new users
    user_id = instance.id if instance.id else 'temp'
    filename = f"avatar_{user_id}.{ext}"
    return os.path.join('avatars', f"user_{user_id}", filename)


class UserManager(BaseUserManager):
    use_in_migrations = True


    def create_user(self, username, password = None, email = None, first_name = None,
                    last_name = None, role = "software_engineer", **extra_fields):
        """
        Create and save a regular user with the given username and password.
        """
        if not username:
            raise ValueError("The username must be set")

        # Normalize username to a consistent form (lowercase)
        username = self.normalize_username(username)
        email = self.normalize_email(email) if email else None  # BaseUserManager has normalize_email

        extra_fields.setdefault('is_active', True)
        user = self.model(
            username=username,
            email=email,
            first_name=first_name or "",
            last_name=last_name or "",
            role=role,
            **extra_fields
        )
        if password:
            user.set_password(password)
        else:
            raise ValueError("User must have a password.")
        user.save(using=self._db)
        return user


    def create_superuser(self, username, password = None, email = None, **extra_fields):
        """
        Create and save a superuser with the given username and password.
        """
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if not password:
            raise ValueError("Superuser must have a password.")

        return self.create_user(username, password, email=email, role="admin", **extra_fields)


    def normalize_username(self, username):
        """
        Normalize the username by lowercasing and stripping whitespace.
        """
        return username.strip().lower() if username else None


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses username instead of email for authentication.
    """
    ROLE_CHOICES = [
        ("product_manager", "Product Manager"),
        ("admin", "Admin"),
        ("software_engineer", "Software Engineer"),
        ("software_architect", "Software Architect"),
        ("data_engineer", "Data Engineer"),
    ]

    username_validator = UnicodeUsernameValidator()
    email_validator = EmailValidator()

    # Authentication fields
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[username_validator],
        verbose_name="Username",
        help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
        db_index=True,  # Index for faster lookups
    )

    email = models.EmailField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        validators=[email_validator],
        verbose_name="Email address",
        help_text="Optional. Used for notifications and password resets.",
        db_index=True,  # Index for faster lookups
    )

    # Personal information
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="First name",
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Last name",
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="software_engineer",
        verbose_name="Role",
        help_text="User's role in the organization.",
        db_index=True,  # Index for role-based queries
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Phone number",
        help_text="Optional phone number.",
    )

    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Bio",
        help_text="Brief description about the user.",
    )

    # Note: Requires Pillow to be installed for ImageField
    # Install with: pip install Pillow
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        verbose_name="Avatar",
        help_text="User profile picture. Requires Pillow to be installed. "
                  "Files are saved to: media/avatars/user_{id}/avatar_{id}.{ext}",
    )

    # Status fields
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Designates whether this user should be treated as active. "
                  "Unselect this instead of deleting accounts.",
        db_index=True,
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name="Staff status",
        help_text="Designates whether the user can log into this admin site.",
    )

    is_email_verified = models.BooleanField(
        default=False,
        verbose_name="Email verified",
        help_text="Designates whether the user's email has been verified.",
    )

    # Timestamps
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date joined",
        help_text="When the user account was created.",
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last updated",
        help_text="When the user account was last modified.",
    )

    last_activity = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Last activity",
        help_text="When the user was last active.",
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # Email can be optional, but you can add it here if needed


    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
            models.Index(fields=['date_joined']),
            models.Index(fields=['username', 'is_active']),  # Composite index for common queries
        ]
        # Note: related_name for groups and permissions is set via PermissionsMixin


    def __str__(self):
        return self.username


    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return full_name if full_name else self.username


    def get_short_name(self):
        """
        Return the short name for the user.
        """
        return self.first_name or self.username


    @property
    def full_name(self):
        """
        Property to get the user's full name.
        """
        return self.get_full_name()


    def clean(self):
        """
        Custom validation for the model.
        """
        super().clean()
        if self.email:
            self.email = User.objects.normalize_email(self.email)


    def save(self, *args, **kwargs):
        """
        Override save to ensure email is normalized.
        """
        if self.email:
            self.email = User.objects.normalize_email(self.email)
        self.full_clean()
        super().save(*args, **kwargs)
