from datetime import datetime 
import random

from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework import status, viewsets

from escrow_app.services import serializers
from escrow_app import permissions, models, utils, tasks

from .utils import compute_total_amount, compute_escrow_transaction_fee

class GetUserName(APIView):
    '''
    Retrieves seller fullname when user ID is passed
    '''  
    serializer_class = serializers.UserNameSerializers
    permission_classes = [permissions.IsActiveVerifiedAuthenticated]
    def get(self, request):
        id = request.query_params.get('id')
        try:
            serialized_data = self.serializer_class(models.UserProfile.objects.get(user__reference_id=id))
            return utils.CustomResponse.Success(serialized_data.data, status=status.HTTP_200_OK)
        except:
            return utils.CustomResponse.Failure("User Name not found",status=status.HTTP_400_BAD_REQUEST)
    
class BuyerTransactionView(APIView):
    '''
    This view handles Buyer and Seller transactions
    '''
    serializer_class = serializers.TransactionSerializer
    permission_classes = [permissions.IsActiveVerifiedAuthenticated]
    
    def get(self, request):
        '''Retrive Transaction for'''
        serialized_data = self.serializer_class(
            models.Transaction.objects.get(Transaction_id=request.data['id']))
        return utils.CustomResponse.Success(serialized_data.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        '''Save details of transaction'''
        # validate that user details are updated
        if not request.user.is_updated:
            return utils.CustomResponse.Failure("Cannot perform this transaction",status=status.HTTP_400_BAD_REQUEST)
        
        partner_id = request.data.get('partner_id')
        buyer_id = request.user.reference_id
        transaction_duration = request.data.get('transaction_duration')
        product_list = request.data.get('product_list')
        product_total_amount = compute_total_amount(product_list)
        escrow_fee = compute_escrow_transaction_fee(product_list)
        transaction_total_amount = (product_total_amount+escrow_fee)
        # save to db using atomicity
        with transaction.atomic():
            try:
                trans = models.Transaction.objects.create(
                    transaction_duration=transaction_duration,
                    buyer_id=buyer_id,
                    seller_id=partner_id,
                    product_list=product_list,
                    product_total_amount=product_total_amount,
                    transaction_total_amount=transaction_total_amount,
                    Initiator=request.user
                )
                data = {
                    "Transaction_id": trans.Transaction_id
                }
                # send product details to celery for saving in a Product table
                tasks.process_transaction_product.delay(product_list, trans.Transaction_id)
                return utils.CustomResponse.Success(data, status=status.HTTP_201_CREATED)
            except:
                return utils.CustomResponse.Failure("Invalid Form", status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        '''endpoint to authorize/accept transaction terms by Actor'''
        transaction_id = request.data.get('id', None)
        transaction_status = request.data.get('Approval', None)
        models.Transaction.objects.filter(
            Transaction_id=transaction_id).update(buyer_approval=transaction_status)
        # create Product_Price_History Object
        if transaction_status == True:
            # Notify Seller of transaction Approval
            deserialized_data = self.serializer_class(
                models.Transaction.objects.get(Transaction_id=transaction_id))
            # create transaction order
            tasks.create_transaction_order.delay(deserialized_data.data)
            # send task to celery
            # send_price_change_notification_task.delay(deserialized_data.data, 'Site', False)
            return utils.CustomResponse.Success(data="Kindly wait for seller's Approval", status=status.HTTP_201_CREATED)
        models.Transaction.objects.filter(
            Transaction_id=transaction_id).update(Transaction_status='Canceled')
        # notify Seller of Canceled Transaction
        deserialized_data = self.serializer_class(
            models.Transaction.objects.get(Transaction_id=transaction_id))
        # send_price_change_notification_task.delay(deserialized_data.data, 'Site', False)
        return utils.CustomResponse.Success(data="Transaction Canceled successfully", status=status.HTTP_200_OK)

class SellerTransactionView(viewsets.ViewSet):
    
    serializer_class = serializers.TransactionSerializer
    permission_classes = [permissions.IsActiveVerifiedAuthenticated]
    
    def list(self, request):
        serialized_data = self.serializer_class(
            models.Transaction.objects.filter(
                seller_id=request.user.reference_id, buyer_approval=True,Transaction_status='Open'),many=True)
        return utils.CustomResponse.Success(serialized_data.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, id):
        serialized_data = self.serializer_class(
            models.Transaction.objects.get(Transaction_id=id))
        return utils.CustomResponse.Success(serialized_data.data, status=status.HTTP_200_OK)
    
    def update(self, request, id):
        transaction_status = request.data.get('seller_approval', None)
        rejection_note = request.data.get('Rejection_note', None)
        models.Transaction.objects.filter(
            Transaction_id=id).update(seller_approval=transaction_status,Actor=request.user,rejection_note=rejection_note)
        # check approval status
        if transaction_status == True:
            # Notify buyer of transaction Approval
            deserialized_data = self.serializer_class(
                models.Transaction.objects.get(Transaction_id=id))
            # send task to celery
            # send_price_change_notification_task.delay(deserialized_data.data, 'Site', False)
            return utils.CustomResponse.Success(data="Transaction Approved, Wait for buyer's payment", status=status.HTTP_201_CREATED)
        models.Transaction.objects.filter(
            Transaction_id=id).update(Transaction_status='Canceled')
        # notify buyer of Canceled Transaction
        deserialized_data = self.serializer_class(
            models.Transaction.objects.get(Transaction_id=id))
        # send_price_change_notification_task.delay(deserialized_data.data, 'Site', False)
        return utils.CustomResponse.Success(data="Transaction Canceled successfully", status=status.HTTP_200_OK)

class Payment(APIView):
    '''A class that handles paystack payments'''
    
    def post(self, request):
        # paystack api endpoint
        url = "https://api.paystack.co/transaction/initialize"

        reference = f"SLN{datetime.datetime.now()}{random.randint(1,10)}"
        callbackurl = get_current_site(request).domain+reverse('')
        fields = {
            "email": request.data["email"],
            "amount": int(request.data["amount"]*100),
            "reference": reference,
            "callback": callbackurl
        }