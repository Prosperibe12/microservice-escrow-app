from django.urls import path
from escrow_app.services import views 

urlpatterns = [
    path("user_name/", views.GetUserName.as_view(), name='user_name'),
    path("new/", views.BuyerTransactionView.as_view(), name='new_transaction')
]