import random
import datetime
import secrets

from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog

from rest_framework_simplejwt.tokens import RefreshToken

from escrow_app.helpers.models import HelperModel
from escrow_app.services.paystack import PayStack

class MyUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

class User(HelperModel,AbstractBaseUser,PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Email and password are required.
    """
    email = models.EmailField(_("email address"), blank=False, null=False, unique=True)
    reference_id = models.IntegerField(_("User Reference ID"), blank=True, null=True, unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_verified = models.BooleanField(
        _("Verified Status"),
        default=False,
        help_text=_("Designates whether the user is verified and can log into his/her account."),
    )
    is_updated = models.BooleanField(
        _("Updated Status"),
        default=False,
        help_text=_("Designates whether the user has updated his/her account and can perform task."),
    )
    date_joined = models.DateTimeField(_("date joined"),auto_now_add=True)

    objects = MyUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    def __str__(self):
        return f"{self.email}"

    # generate unique reference_id for user
    def save(self, *args, **kwargs):
        while not self.reference_id:
            nos = str(random.randint(1,7))
            nrs = [str(random.randrange(10)) for i in range(6-1)]
            for i in range(len(nrs)):
                nos += str(nrs[i])
            ref_id = User.objects.filter(reference_id=nos)
            if not ref_id:
                self.reference_id=nos
        super(User, self).save(*args, **kwargs) # Call the real save() method

    # user tokens
    def tokens(self):
        tokens = RefreshToken.for_user(self)
        return {
            'refresh': str(tokens),
            'access': str(tokens.access_token)
        }

auditlog.register(model=User, exclude_fields=['password', 'last_login'])

class UserProfile(HelperModel,models.Model):
    '''
    User Profile Table
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    full_name = models.CharField(_("full name"), max_length=150, blank=False, null=False, default="Hello User")
    phone_number = models.CharField(_("Phone Number"), blank=False, null=False, max_length=14)
    address = models.CharField(_("Residential address"), blank=False, max_length=150, null=False)
    state = models.CharField(_("State of residence"), blank=False, max_length=150, null=False)
    lga = models.CharField(_("local govt area"), max_length=150, blank=False, null=False, default="lga")
    profile_pix = models.ImageField(_("profile image"), upload_to='profile_img', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['png','jpeg','jpg'])])
    
    def __str__(self) -> str:
        return f"{self.first_name}::{self.last_name}"

class Transaction(HelperModel,models.Model):
    """Transaction Record Table"""
    duration = (
        ('1-3 Days', '1-3 Days'),
        ('3-5 Days', '3-5 Days'),
        ('7-14 Days', '7-14 Days'),
    )
    status = (
        ('Open', 'Open'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled')
    )
    Transaction_id = models.BigAutoField(primary_key=True)
    transaction_duration = models.CharField(choices=duration, max_length=200, blank=False, null=False)
    buyer_id = models.CharField(max_length=100,blank=False,null=False)
    seller_id = models.CharField(max_length=100,blank=True,null=True)
    product_list = models.TextField(blank=False,null=False)
    product_total_amount = models.DecimalField(max_digits=12,decimal_places=2,blank=True,null=True)
    transaction_total_amount = models.DecimalField(max_digits=12,decimal_places=2,blank=True,null=True)
    buyer_approval = models.BooleanField(default=False,blank=True,null=True)
    seller_approval = models.BooleanField(default=False,blank=True,null=True)
    Initiator = models.ForeignKey(User,on_delete=models.CASCADE,related_name="transaction_initiator",null=True,blank=True)
    Actor = models.ForeignKey(User,on_delete=models.CASCADE,related_name="transaction_actor",null=True,blank=True)
    Transaction_status = models.CharField(choices=status, max_length=200, blank=False, null=False, default='Open')
    rejection_note = models.CharField(max_length=250,blank=True,null=True)
    
    def __str__(self) -> str:
        return f'{self.Transaction_id}'
class Product(models.Model):
    category = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    Transaction = models.ForeignKey(Transaction,related_name="transaction_product",on_delete=models.CASCADE,blank=False,null=False)
    
    def __str__(self) -> str:
        return f"{self.id}::{Transaction}"

class Order(HelperModel,models.Model):
    '''This table holds record of payment transactions'''
    ORDER_STATUS = (
        ('Order Created', 'Order Created'),
        ('Payment Completed', 'Payment Completed'),
        ('Order Canceled', 'Order Canceled'),
    )
    Order_id = models.BigAutoField(primary_key=True)
    Transaction_details = models.OneToOneField(Transaction,on_delete=models.CASCADE,blank=True,null=True)
    ref = models.CharField(max_length=200, null=True, blank=True)    
    amount = models.PositiveIntegerField(null=True, blank=True)
    order_status = models.CharField(max_length=200, choices=ORDER_STATUS)
    
    def __str__(self):
        return f'{self.Order_id}::{str(self.Transaction_details)}'
    
    # generate reference code
    def save(self, *args, **kwargs):
        while not self.ref:
            ref = {secrets.token_urlsafe(15)}+{datetime.datetime.now()}
            obj_with_sm_ref = Order.objects.filter(ref=ref)
            if not obj_with_sm_ref:
                self.ref = ref 
        super().save(*args, **kwargs)
          
    # verify payment
    def verify_payment(self):
        
        paystack = PayStack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        
        if status:
            if result['amount']/100 == self.amount:
               self.order_status = 'Payment Received' 
            self.save() 
            return True 
        return False 
        
    
# {
#    "email": "roketragroite-1595@yopmail.com",
#    "password": "Password123"
# }