from . import views
from django.urls import path

app_name = 'accounts'

urlpatterns = [
    path("google-auth/", views.GoogleSocialAuthView.as_view(), name="google-auth"),\
]
