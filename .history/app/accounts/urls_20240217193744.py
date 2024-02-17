from . import views
from django.urls import path

app_name = 'accounts'

urlpatterns = [
    path("google-social-auth/", views.GoogleSocialAuthView.as_view(), name="google-social-auth"),\
    path("add-order/", views.AddOrderView.as_view(), name="add-order"),\
]
