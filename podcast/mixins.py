from account.models import User
from django.http.response import Http404


class AccessSuperUserMixin:

    def dispatch(self, request, *args, **kwargs):
        current_user = request.user
        if current_user.is_superuser and isinstance(current_user, User):
            return super(AccessSuperUserMixin, self).dispatch(request)
        raise Http404("access denied")
