from django.urls import path
from escrow_app.services import views 

urlpatterns = [
    path("user_name/", views.GetUserName.as_view(), name='user_name'),
    path("new/", views.BuyerTransactionView.as_view(), name='new_transaction'),
    path("open/", views.SellerTransactionView.as_view({'get':'list'}), name='open_transactions'),
    path("open/<str:id>/", views.SellerTransactionView.as_view({'get':'retrieve','put':'update'}),name='single_open_transaction'),
    path("pending/", views.Payment.as_view({'get':'list','post':'create'}), name='pending_transactions'),
    path("pending/<str:id>/", views.Payment.as_view({'get':'retrieve'}), name='payment'),
    path("<str:ref>/", views.verify_payment, name='verify_payment')
]