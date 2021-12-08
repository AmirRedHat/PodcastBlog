from django.forms import ModelForm, Form, fields
from .models import User

class CreateUserForm(ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name",
        "email", "password", "birth_day", "avatar", "biography")


class LoginUserForm(Form):
    email = fields.CharField(max_length=300)
    password = fields.CharField(max_length=300)