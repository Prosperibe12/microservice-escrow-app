from rest_framework import serializers
from escrow_app import models

class UserNameSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ['full_name']
        model = models.UserProfile

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = models.Transaction
        
class PaymentSerializer(serializers.ModelSerializer):
    order_ref = serializers.SerializerMethodField()
    class Meta:
        fields = ['Transaction_id','transaction_duration','buyer_id','seller_id','product_list',
                  'product_total_amount','transaction_total_amount','buyer_approval','seller_approval','Transaction_status',
                  'Initiator','Actor','order_ref']
        model = models.Transaction
        
    def get_order_ref(self, obj):
        try:
            ref = models.Order.objects.get(Transaction_details=obj.Transaction_id).values('ref')
        except:
            ref = None
        return ref