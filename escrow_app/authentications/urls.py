from django.urls import path 
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from escrow_app.authentications import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='register')
]