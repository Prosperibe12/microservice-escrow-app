from rest_framework import serializers

from escrow_app import models

class UserSerializer(serializers.Serializer):
    
    reference_id = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    is_updated = serializers.BooleanField(read_only=True)

class UserDetailSerializer(serializers.ModelSerializer):
    
    owner = UserSerializer(source='user')
    
    class Meta:
        model = models.UserProfile
        fields = ['owner','full_name', 'phone_number', 'address', 'state', 'lga']

class UpdateUserDataSerializer(serializers.ModelSerializer):
    
    profile_pix = serializers.ImageField(required=False, write_only=True)
    full_name = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    lga = serializers.CharField(required=False)
    
    class Meta:
        model = models.UserProfile
        fields = ['full_name','phone_number','address','state','lga','profile_pix']