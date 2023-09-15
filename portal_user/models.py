import math
import random
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .token import account_activation_token

from electricity_bill_management_system.settings import CLIENT_DOMAIN

# Create your models here.


class PortalUserManager(BaseUserManager):
    def _create_portal_user(self, email, password, is_superuser=False,  **kwargs):
        if not email:
            raise ValueError("Email is required!")

        if not password:
            raise ValueError("Password is required!")

        user_role = "0" if is_superuser else "1"
        portal_user = self.model(email=self.normalize_email(
            email), is_superuser=is_superuser, user_role=user_role, **kwargs)
        portal_user.set_password(password)
        portal_user.save()
        return portal_user

    def create(self, email, password, **kwargs):
        return self._create_portal_user(email=email, password=password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        return self._create_portal_user(email=email, password=password, is_superuser=True, **kwargs)


class PortalUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, blank=False, unique=True)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=True, default="")
    phone_number = models.CharField(max_length=12, blank=True, default="")
    consumer_or_staff_id = models.CharField(max_length=20,
                                            unique=True, db_index=True, null=True, blank=True)

    USER_ROLE = (("0", "Staff"), ("1", "Consumer"))

    user_role = models.CharField(max_length=1, choices=USER_ROLE, default="0")

    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    otp = models.CharField(max_length=10, blank=True, default="")

    failed_login_attempt = models.PositiveIntegerField(default=0, blank=False)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = PortalUserManager()

    def __str__(self) -> str:
        full_name = f"{self.first_name.strip()} {self.last_name.strip()}"
        return f"{full_name} ({self.email})"

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def get_short_name(self) -> str:
        return f"{self.first_name.strip()}"

    def get_full_name(self) -> str:
        return f"{self.first_name.strip()} {self.last_name.strip()}"

    def send_welcome_email(self):
        mail_subject = 'Welcome to Our Platform'
        mail_message = render_to_string('portal_user/welcome_email.html', {
            "first_name": f"{self.first_name}!",
        })

        try:
            email = EmailMessage(
                subject=mail_subject, body=mail_message, to=[self.email]
            )
            email.content_subtype = "html"
            email.send()
        except BadHeaderError:
            return HttpResponse("Invalid header found!")
        except Exception as e:
            return HttpResponse("Something went wrong!")

    def send_account_activation_mail(self):
        mail_subject = 'Welcome to Our Platform! Activate Your Account'
        mail_message = render_to_string('portal_user/account_activate_email.html', {
            "first_name": f"{self.first_name}!",
            "uidb64": urlsafe_base64_encode(force_bytes(self.pk)),
            "token": account_activation_token.make_token(self),
            "activate_url": CLIENT_DOMAIN
        })

        try:
            email = EmailMessage(
                subject=mail_subject, body=mail_message, to=[self.email]
            )
            email.content_subtype = "html"
            email.send()
        except BadHeaderError:
            return HttpResponse("Invalid header found!")
        except Exception as e:
            return HttpResponse("Something went wrong!")

    def generate_otp(self):
        digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.otp = ""

        for i in range(6):
            self.otp += digits[int(math.floor(random.random() * len(digits)))]
        self.save()

        mail_subject = "OTP To Login On Our Platform"
        mail_message = render_to_string(
            "portal_user/send_otp_email.html", {"first_name": f"{self.first_name}!",
                                                "otp": str(self.otp)}
        )

        try:
            email = EmailMessage(
                subject=mail_subject, body=mail_message, to=[self.email]
            )
            email.content_subtype = "html"
            email.send()
        except BadHeaderError:
            return HttpResponse("Invalid header found!")
        except Exception as e:
            return HttpResponse("Something went wrong!")
