from django.http.response import Http404
from django.shortcuts import get_object_or_404

from .models import User


class UserMixin:

    def dispatch(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        if not pk:
            pk = request.POST.get("pk")

        if request.session["session_key"] is not None and request.is_authenticate:
            if int(request.user.id) == int(pk):
                return super(UserMixin, self).dispatch(request)
            raise Http404(f"you cannot access to this part.", )
        raise Http404("you are not login")


class LoginMixin:

    def dispatch(self, request, *args, **kwargs):
        if isinstance(request.user, User):
            return super(LoginMixin, self).dispatch(request)
        else:
            raise Http404("You are not logged in")


class SuperUserMixin:

    def dispatch(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        if not pk:
            pk = request.POST.get("pk")

        user = get_object_or_404(User, pk=pk)
        if user.is_superuser and user.is_staff:
            return super(SuperUserMixin, self).dispatch(request)
        raise Http404("you cannot access to this part.\nyou are not an super user")
