from django.urls import path
from . import views


app_name = "Account"
urlpatterns = [
    path("all-users", views.AllUsers.as_view(), name="all_users"),

    path("<int:pk>", views.SingleUser.as_view(), name="single"),
    path("signup/", views.Signup.as_view(), name="signup"),
    path("login", views.Login.as_view(), name="login"),
    path("logout", views.Logout.as_view(), name="logout"),
    path("delete/<int:pk>", views.DeleteUser.as_view(), name="delete"),
    path("update/<int:pk>", views.UpdateUser.as_view(), name="update"),
    path("follow/", views.FollowUser.as_view(), name='follow'),
    path("change_password/", views.ChangePassword.as_view(), name="change_password"),
    path("search/user/<search_word>", views.SearchUser.as_view(), name="search_user"),
    path("podcasts/<int:pk>", views.UserPodcasts.as_view(), name="user_podcast"),
    path("email_verification/", views.EmailVerification.as_view(), name="email_verification"),
]
