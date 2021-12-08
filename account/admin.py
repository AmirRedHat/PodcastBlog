from django.contrib import admin
from .models import User, IPAddress, Code
# Register your models here.

admin.site.register(User)
admin.site.register(IPAddress)
admin.site.register(Code)