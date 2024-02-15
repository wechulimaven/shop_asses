from . import views
from django.urls import path

app_name = 'accounts'

urlpatterns = [
    path("login/", views.TokenLoginView.as_view(), name="token-login"),
    path("google-auth/", views.GoogleSocialAuthView.as_view(), name="google-auth"),
    path("admin-login/", views.AdminTokenLoginView.as_view(), name="admin-token-login"),
    path("logout/", views.TokenLogoutView.as_view(), name="token-logout"),
    path("registration/", views.AccountRegistrationView.as_view(), name="account-registration"),
    path("update-account/", views.UpdateUserAccountView.as_view(), name="update-account-registration"),
    path("change-account-passoword/", views.ChangeAccountPasswordView.as_view(), name="change-account-passoword"),
    path("forgot-passoword/", views.ForgotPasswordView.as_view(), name="forgot-passoword"),
    path("reset-passoword/", views.ResetAccountPasswordView.as_view(), name="reset-passoword"),
    path("get-users/", views.GetAllUsers.as_view(), name='get-users'),
    path("get-loggedin-user/", views.GetLoggedInUserDetail.as_view(), name='get-loggedin-user'),
    path("user-detail/<str:id>/", views.GetUserDetail.as_view(), name='user-detail'),

    path("subscription/", views.UserSubscriptionView.as_view(), name='subscription')
]
