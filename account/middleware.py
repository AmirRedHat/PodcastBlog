from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404

from .models import User, IPAddress


class SetRequestUserMiddleware:

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        try:
            session_key = request.session["session_key"]
            if session_key is not None:
                # user = User.objects.get(pk=session_key)
                user = get_object_or_404(User, pk=session_key)
                request.user = user
                request.is_authenticate = True
            else:
                request.user = AnonymousUser()
                request.is_authenticate = False

        except:
            request.session["session_key"] = None

        response = self.get_response(request)
        return response


class IpAddressMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        x_http_forward = request.META.get("HTTP_X_FORWARD_FOR")

        try:
            ip = x_http_forward.split(",")[0]
        except:
            ip = request.META.get("REMOTE_ADDR")

        if not IPAddress.objects.filter(ip_address=ip).exists():
            ip_address = IPAddress()
            ip_address.ip_address = ip

            if isinstance(request.user, User):
                ip_address.user = request.user

            ip_address.save()
        else:
            ip_address = get_object_or_404(IPAddress, ip_address=ip)

        request.ip_address = ip_address

        response = self.get_response(request)
        return response
