from django.db import models

class HelperModel(models.Model):
    '''
    Automatically creates these attributes when this class is inherited
    '''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True