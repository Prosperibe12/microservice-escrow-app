from django.contrib import admin
from escrow_app import models

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'reference_id',
        'is_staff',
        'is_verified',
        'is_updated',
    )
admin.site.register(models.User, UserAdmin)

class UserProfileAdmin(admin.ModelAdmin):
        list_display = (
        'user',
        'full_name',
        'phone_number',
        'address',
        'state',
        'profile_pix',
    )
admin.site.register(models.UserProfile, UserProfileAdmin)