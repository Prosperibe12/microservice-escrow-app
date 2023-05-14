from django.urls import path

from . import views

urlpatterns = [
    path('profile/', views.UserProfile.as_view(), name='user-profile'),
    path('update/', views.UpdateUserProfile.as_view(), name='update-profile')
]