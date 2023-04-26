from django.urls import path, include

urlpatterns = [
    path('auth/', include('escrow_app.authentications.urls'))
]