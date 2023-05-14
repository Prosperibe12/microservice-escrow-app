from __future__ import absolute_import, unicode_literals
from celery import shared_task

from escrow_app.authentications import utils

'''
**************************************************************************
AUTHENTICATION CELERY TASKS
***************************************************************************
'''
@shared_task(name='app-verify-email')
def email_verification_link(user,domain_name):
    notifier = utils.AuthNotificationFactory()
    # trigger register_email_notification method
    if notifier is not None:
        notifier.register_email_notification(user,domain_name)

@shared_task(name='app-password-reset-link')
def password_reset_link(users, domain_name):
    sender = utils.AuthNotificationFactory()
    # trigger register_email_notification method
    if sender is not None:
        sender.send_password_reset_email(users, domain_name)
