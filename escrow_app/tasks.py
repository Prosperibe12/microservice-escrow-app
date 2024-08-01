from __future__ import absolute_import, unicode_literals
from celery import shared_task

from escrow_app.authentications.utils import AuthNotificationFactory
from escrow_app.services import utils
from escrow_app.notifications import utils as ut

'''
**************************************************************************
AUTHENTICATION CELERY TASKS
***************************************************************************
'''
@shared_task(name='app-verify-email')
def email_verification_link(token,domain_name):
    notifier = AuthNotificationFactory()
    # trigger register_email_notification method
    if notifier is not None:
        notifier.register_email_notification(token,domain_name)

@shared_task(name='app-password-reset-link')
def password_reset_link(users, domain_name):
    sender = AuthNotificationFactory()
    # trigger register_email_notification method
    if sender is not None:
        sender.send_password_reset_email(users, domain_name)

'''
**************************************************************************
TRANSACTION CELERY TASKS
***************************************************************************
'''
@shared_task(name='process_transaction_products')
def process_transaction_product(data,trans):
    '''This task handles the process of saving transaction products asynchronously'''
    utils.product_transaction(data,trans)
    
@shared_task(name='create_transaction_order')
def create_transaction_order(data):
    utils.create_transaction_order(data)

'''
**************************************************************************
NOTIFICATION CELERY TASKS
***************************************************************************
'''
@shared_task(name='send_buyer_transaction_approval')
def send_buyer_transaction_approval(approval_request, designation, status):
    # Use factory to get a Transaction Alarm notifier class based on the Approval Status and Designation(Buyer/Seller)
    notifier = ut.NotificationAlarmFactory(
        approval_request, designation, status).create_alarm_notifier()
    # trigger notifier notify method
    if notifier is not None:
        notifier.notify()