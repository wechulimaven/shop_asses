from . import views
from django.urls import path

app_name = 'accounts'

urlpatterns = [
    path("google-auth/", views.GoogleSocialAuthView.as_view(), name="google-auth"),
    path("login/", views.TokenLoginView.as_view(), name="token-login"),
    path("logout/", views.TokenLogoutView.as_view(), name="token-logout"),
    path("registration/", views.AccountRegistrationView.as_view(), name="account-registration"),
    path("get-loggedin-user/", views.GetLoggedInUserDetail.as_view(), name='get-loggedin-user'),
]
