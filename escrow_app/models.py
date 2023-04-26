from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog
from escrow_app.helpers.models import HelperModel

from rest_framework_simplejwt.tokens import RefreshToken

class MyUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

class User(HelperModel,AbstractBaseUser,PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Email and password are required. Other fields are optional.
    """
    first_name = models.CharField(_("first name"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True, null=True)
    email = models.EmailField(_("email address"), blank=False, null=False, unique=True)
    phone_number = models.CharField(_("Phone Number"), blank=False, null=False, max_length=14)
    address = models.CharField(_("Residential address"), blank=True, max_length=150, null=True)
    state = models.CharField(_("State of residence"), blank=True, max_length=150, null=True)
    profile_pix = models.ImageField(_("profile image"), upload_to='profile_img', null=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_verified = models.BooleanField(
        _("Verified Status"),
        default=False,
        help_text=_("Designates whether the user is verified and can log into his/her account."),
    )
    is_updated = models.BooleanField(
        _("Updated Status"),
        default=False,
        help_text=_("Designates whether the user has updated his/her account and can perform task."),
    )
    date_joined = models.DateTimeField(_("date joined"),auto_now_add=True)

    objects = MyUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]

    def __str__(self):
        return f"{self.email}"

    def tokens(self):
        tokens = RefreshToken.for_user(self)
        return {
            'refresh': str(tokens),
            'access': str(tokens.access_token)
        }

auditlog.register(model=User, exclude_fields=['password', 'last_login'])
