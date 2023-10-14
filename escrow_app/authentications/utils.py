import requests
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from decouple import config
from django.urls import reverse

from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.tokens import RefreshToken

from escrow_app import models, utils

class AuthNotificationFactory:
    
    @staticmethod
    def register_email_notification(payload,domain_name):
        try:
            user = models.User.objects.get(email=payload['email'])
        except:
            models.User.DoesNotExist
        token = RefreshToken.for_user(user).access_token
        url_path = reverse('verify-email')
        subject = f"ACCOUNT VERIFICATION"
        absurl = 'http://'+domain_name+url_path+'?token='+str(token)
        message = f"Hello, \n Kindly use below link to activate your email \n  {absurl}"
        print("message: ",message)
        try:
            msg = requests.post(
                config("MAIL_BASE_URL"), 
                auth=("api", config("MAILGUN_SECRET_KEY")), 
                data = {"from": config("MAIL_SENDER"), "to": [payload['email']], "subject": subject, "text": message}
            )
            return msg
        except Exception as e:
            print(e)
    
    @staticmethod 
    def send_password_reset_email(users, domain_name):
        # get user
        try:
            user = models.User.objects.get(email=users['email'])
        except:
            raise NotFound('Inactive User or User Does Not Exist.')
        
        if not user.is_active:
            return utils.CustomResponse.Failure("Inactive User")
        
        # encode user object and create a password reset token for user
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        abs_path = reverse('password_reset_confirm', kwargs={'uidb64':uidb64, 'token':token})

        subject = f"PASSWORD RESET REQUEST"
        absurl = 'http://'+domain_name+abs_path
        message = f"Hello, \n Kindly use below link to reset your password \n {absurl}"
        print("Password reset :",message)
        # send email
        try:
            msg = requests.post(
                config("MAIL_BASE_URL"), 
                auth=("api", 
                config("MAILGUN_SECRET_KEY")), 
                data = {"from": config("MAIL_SENDER"), "to": [user.email], "subject": subject, "text": message}
            )
            return msg
        except Exception as e:
            print(e)