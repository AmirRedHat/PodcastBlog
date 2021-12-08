from django.http.response import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView, ListView, DeleteView, View, FormView
from django.db.models import Q
from django.core import serializers

from .models import login, logout, UserAuthentication, Code
from .mixins import UserMixin
from .forms import *
from podcast.models import Podcast


# Create your views here.


class SingleUser(DetailView):
    model = User
    context_object_name = "user"
    template_name = "single_user.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["birth_day"] = None
        return context


class AllUsers(ListView):
    model = User
    template_name = "all_users.html"
    context_object_name = "users"


class Signup(FormView):
    form_class = CreateUserForm
    template_name = "signup.html"

    def form_valid(self, form, *args, **kwargs):
        instance = form.save(commit=False)
        instance.set_password()
        instance.save()
        # return redirect("Account:single", pk=instance.pk)
        return redirect("Account:email_verification")


class Login(FormView):
    form_class = LoginUserForm
    template_name = "login.html"

    def form_valid(self, form, *args, **kwargs):
        email, password = form.cleaned_data["email"], form.cleaned_data["password"]
        user = UserAuthentication().authenticate(email=email, password=password)
        if user:
            login(self.request, user)
            return redirect("Podcast:podcasts")
        raise Http404("Email or Password is invalid")


class Logout(View):

    def get(self, *args, **kwargs):
        logout(self.request)
        return redirect("Podcast:podcasts")


class DeleteUser(UserMixin, DeleteView):
    model = User
    success_url = "/"


class UpdateUser(View):
    template_name = "update_user.html"

    def post(self, *args, **kwargs):
        data = self.request.POST
        pk = kwargs.get("pk")

        get_user = get_object_or_404(User, pk=pk)
        update = get_user.user_manager(data=data)
        get_user.save()
        print("update message: ", update)

        if not update:
            raise Http404(update)
        return redirect("Account:single", pk=pk)

    def get(self, *args, **kwargs):
        get_user = get_object_or_404(User, pk=kwargs.get("pk"))
        context = {"user": get_user}
        return render(self.request, self.template_name, context)


class FollowUser(View):

    def post(self, *args, **kwargs):
        user_pk = self.request.POST.get("user_pk")
        user = get_object_or_404(User, pk=user_pk)
        rq_user = self.request.user

        if rq_user.is_follow(user):
            print("Unfollowing")
            rq_user.unfollow(user)
            status_follow = 'follow'
        else:
            print("Following")
            rq_user.follow(user)
            status_follow = "unfollow"

        return JsonResponse({'data': status_follow})


class ChangePassword(View):
    template_name = "change_password.html"

    def get(self, *args, **kwargs):
        return render(self.request, self.template_name, {})

    def post(self, *args, **kwargs):

        request_post = self.request.POST
        current_email = self.request.user.email
        current_password = request_post["current_password"]
        new_password = request_post["new_password"]
        confirm_new_password = request_post["confirm_new_password"]

        if new_password != confirm_new_password:
            raise Http404("New Password field is not equal to Confirm New Password")

        user_authentication = UserAuthentication()
        user = user_authentication.authenticate(email=current_email, password=current_password)
        if isinstance(user, User):
            user.set_password(password=new_password)
            user.save()
            login(self.request, user)

        return JsonResponse(data={"password_changed": True})


class SearchUser(View):

    @staticmethod
    def get(*args, **kwargs):
        search_word = kwargs.get("search_word")
        search_obj = Q(first_name__contains=search_word) | \
                     Q(last_name__contains=search_word) | \
                     Q(email__contains=search_word)

        searched_users = User.objects.filter(search_obj)
        serialized_data = serializers.serialize("json", searched_users)

        return JsonResponse(data={"user_list": serialized_data, "status": "searched successfully"})


class UserPodcasts(View):

    @staticmethod
    def get(*args, **kwargs):
        user_pk = kwargs.get("pk")
        user = get_object_or_404(User, pk=user_pk)
        podcasts = Podcast.objects.filter(user=user)
        serialized_data = serializers.serialize("json", podcasts)
        return JsonResponse(data={"data": serialized_data, "status": "podcasts got successfully"})


class UserPodcastMark(View):

    def get(self, *args, **kwargs):
        podcasts = Podcast.objects.filter(mark__in=self.request.user)
        return JsonResponse(data={"podcasts": podcasts})


class EmailVerification(View):
    template_name = "email_verification.html"

    def get(self, *args, **kwargs):
        to_address = self.request.user.email
        subject = "Email Verification"
        code_manager = Code()
        code = code_manager.generate_code(user=self.request.user)
        message = (code, subject)
        context = {"email": self.request.user.email}
        code_manager.send_mail(message=message, to_address=to_address)
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        code: str = self.request.POST.get("code")
        if type(code) != str:
            raise Http404("Code format is incorrect")
        code: str = code.strip().lower()
        code_obj = get_object_or_404(Code, code=code, user=self.request.user)
        if code_obj:
            user = get_object_or_404(User, pk=self.request.user.pk)
            user.is_active = True
            user.save()
            return redirect("Account:single", pk=user.pk)
