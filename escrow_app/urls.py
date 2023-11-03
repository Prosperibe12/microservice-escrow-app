from django.urls import path, include

urlpatterns = [
    path('auth/', include('escrow_app.authentications.urls')),
    path('users/', include('escrow_app.users.urls')),
    path('transaction/', include('escrow_app.services.urls')),
]