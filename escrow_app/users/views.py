from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.parsers import (MultiPartParser, FormParser)

from escrow_app import models
from escrow_app.permissions import IsActiveVerifiedAuthenticated
from escrow_app import utils, producer
from escrow_app.users import serializers


class UserProfile(APIView):
    
    '''
    This view allows for users to retrieve and update their profile, user must be authenticated.
    '''
    permission_classes = [IsActiveVerifiedAuthenticated]
    serializer_class = serializers.UserDetailSerializer
    parser_classes = [MultiPartParser, FormParser]
        
    def get(self, request):
        
        try:
            user = models.UserProfile.objects.get(user=request.user)
            serialized_data = self.serializer_class(user)
            return utils.CustomResponse.Success(serialized_data.data, status=status.HTTP_200_OK)
        except:
            return utils.CustomResponse.Failure("User not found", status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        
        if models.UserProfile.objects.filter(user=request.user).exists():
            return utils.CustomResponse.Failure("User Already Exist", status=status.HTTP_400_BAD_REQUEST)
        
        serializer = serializers.UpdateUserDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            user = models.User.objects.get(id=request.user.id)
            user.is_updated = True
            user.save()
            # publish event
            # producer.publish('save_user_profile',serializer.data)
            return utils.CustomResponse.Success(serializer.data, status=status.HTTP_201_CREATED)
        return utils.CustomResponse.Failure(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateUserProfile(APIView):
    '''
    A view that allow users modify existing profile
    '''
    permission_classes = [IsActiveVerifiedAuthenticated]
    serializer_class = serializers.UpdateUserDataSerializer
    
    def put(self, request):
        try:
            user = models.UserProfile.objects.get(user=request.user)
            serializer = self.serializer_class(instance=user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                # publish event
                # producer.publish('update_user_profile',serializer.data)
                return utils.CustomResponse.Success(serializer.data, status=status.HTTP_201_CREATED)
            return utils.CustomResponse.Failure(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return utils.CustomResponse.Failure("User Not Founnd", status=status.HTTP_400_BAD_REQUEST)