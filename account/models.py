from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth import settings
from django.http.response import Http404
from django.contrib.auth.models import UserManager

from hashlib import sha256
import base64
from datetime import datetime, timedelta
import binascii
import os
from smtplib import SMTP, SMTPAuthenticationError
import ssl
from email.message import EmailMessage

# Create your models here.

USER_MODEL = settings.AUTH_USER_MODEL


def login(request, user):
    try:
        if request.session["session_key"] is not None and request.is_authenticated:
            request.is_authenticated = False
            request.session.flush()
            request.session["session_key"] = None
    except Exception as e:
        request.session["session_key"] = None
        print(e)

    request.session["session_key"] = user.id
    request.session.save()


def logout(request):
    request.session.flush()
    request.session["session_key"] = None


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, default=None, null=True, blank=True)
    avatar = models.ImageField(default="default.jpg", upload_to="avatars")
    email = models.EmailField(unique=True)
    biography = models.TextField()
    birth_day = models.DateField(default=None, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    followers = models.ManyToManyField(USER_MODEL, related_name="user_followers", blank=True)
    followings = models.ManyToManyField(USER_MODEL, related_name="user_followings", blank=True)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "password"]

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["birth_day"]),
            models.Index(fields=["date"])
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_fullname(self) -> str:
        return f"{self.first_name}-{self.last_name}"

    def set_password(self, password: str = None) -> None:
        if password is None:
            password = self.password
        self.password = UserAuthentication().hasher(password=password)

    def user_manager(self, data: dict):
        try:
            self.first_name = data["first_name"]
            self.last_name = data["last_name"]
            self.email = data["email"]
            self.biography = data["biography"]
            self.birth_day = data["birth_day"]
            self.avatar = data["avatar"]
            return True
        except Exception as error:
            return error

    def is_follow(self, user):
        """ check following and follower user """
        condition = (user in self.followings.all() and self in user.followers.all())  # noqa
        if condition:
            return True
        else:
            return False

    def follow(self, user):
        try:
            self.followings.add(user)
            user.followers.add(self)
            user.save()
            self.save()
            return True
        except Exception as error:
            return False

    def unfollow(self, user):
        try:
            self.followings.remove(user)
            user.followers.remove(user)
            user.save()
            self.save()
            return True
        except Exception as error:
            return False


class UserAuthentication:

    @staticmethod
    def hasher(password, algorithm="default"):
        password = str(password).encode()
        if algorithm == "default":
            return sha256(password).hexdigest()
        elif algorithm == "base64":
            return str(base64.b64encode(password))

    def authenticate(self, email: str, password: str):
        user = User.objects.get(email=email.strip())
        if user.password == self.hasher(password=password):
            return user
        else:
            raise Http404("email or password is invalid")


class IPAddress(models.Model):
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ipaddress_user", default=None, blank=True,
                             null=True)
    date = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=("ip_address",))
        ]

    def __str__(self) -> str:
        return f"{self.ip_address}"

    # def location(self):
    #     api = "https://freegeoip.app/json/%s" % self.ip_address
    #     response = requests.get(api)
    #     return response.json()


class Code(models.Model):
    code = models.CharField(max_length=50, null=False, blank=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="code_user", default=None)
    expire_date = models.DateTimeField(null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=["expire_date"])
        ]

    def __str__(self):
        return self.code

    @staticmethod
    def generate_code(user: User) -> str:
        """
            generate code ( 7 letter )
        """

        code_obj = Code()
        code_obj.code = binascii.hexlify(os.urandom(3)).decode()
        code_obj.user = user
        now = datetime.now()
        code_obj.expire_date = now + timedelta(minutes=5)
        code_obj.save()
        return code_obj.code

    @staticmethod
    def kill_code(user: User, code: str) -> str:

        code = get_object_or_404(Code, code=code, user=user)
        code.delete()
        return code

    @staticmethod
    def check_code(user: User, code: str):

        now_date = datetime.now()
        expire_date = get_object_or_404(Code, code=code, user=user).expire_date
        if expire_date >= now_date:
            return False
        return True

    @staticmethod
    def is_exists(code):
        if Code.objects.filter(code=code).exists():
            return True
        else:
            return False

    @staticmethod
    def send_mail(*args, **kwargs):
        """ sending email from DEFAULT_EMAIL to user """

        from_address = "amir.ch.charehei1382@gmail.com"  # DEFAULT EMAIL ADDRESS
        from_password = "django%python#"  # DEFAULT EMAIL PASSWORD

        message, to_address = kwargs["message"], kwargs["to_address"]

        body, subject = message
        message = EmailMessage()
        message.set_content(body)
        message["Subject"] = subject
        message["To"] = to_address
        message["From"] = from_address

        context = ssl.create_default_context()
        with SMTP(host="smtp.gmail.com", port=587) as server:
            try:
                server.starttls(context=context)
                server.login(user=from_address, password=from_password)
                server.send_message(message, from_addr=from_address, to_addrs=to_address)
                server.quit()
            except SMTPAuthenticationError:
                raise Http404("email authentication error")
