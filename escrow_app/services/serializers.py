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