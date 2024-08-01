import requests
from django.template import loader

from escrow_app import models
# from twilio.rest import Client
from decouple import config

# from backend.notifications import utils
# config('REPORT_DELAY_ACTIVE', cast=bool)
# account_sid = config('TWILIO_ACCOUNT_SID')
# auth_token = config('TWILIO_AUTH_TOKEN')
# client = Client(account_sid, auth_token)


class TransactionAlarmNotifier:
    """
    Transaction Alarm Notifier.
    """
    alarm_type = ''
    email_template_name = ''
    email_subject = ''
    mail_list = ''
    phone_msg_template = ''
    push_notification_msg_template = ''
    # initialize variables
    def __init__(self, approval_request):
        
        self.approval_request = approval_request
        transaction_initiator = models.UserProfile.objects.get(user=self.approval_request['Initiator']).full_name
        transaction_approver = models.UserProfile.objects.get(user=self.approval_request['Actor']).full_name
        self.context = {
            'price': self.approval_request['product_total_amount'],
            'sheduled_time': self.approval_request['transaction_duration'],
            'Initiator': transaction_initiator,
            'approver': transaction_approver,
            'rejection_note': self.approval_request['rejection_note'],
            "created_time": self.approval_request['created_at'],
        }

      
    def __init__(self, price_change):
        self.price_change = price_change

        try:
            this_company = self.price_change['Company']
            company_obj = models.Companies.objects.get(pk=this_company).Name
        except:
            company_obj = None

        price_initiator = models.User.objects.get(
            pk=self.price_change['Initiator']).Name
        product_name = models.Products.objects.get(
            pk=self.price_change['Product']).Name
        try:
            price_change_approver = models.User.objects.get(
                pk=self.price_change['Actor']).Name
        except models.User.DoesNotExist:
            price_change_approver = None
        try:
            site_name = (models.Sites.objects.get(
                pk=self.price_change['Site'])).Name
        except KeyError:
            site_name = None

        self.context = {
            'product_name': product_name,
            'price': self.price_change['New_price'],
            'sheduled_time': self.price_change['Scheduled_time'],
            'Initiator': price_initiator,
            'approver': price_change_approver,
            'rejection_note': self.price_change['Rejection_note'],
            'company_name': company_obj,
            'site_name': site_name,
            "updated_time": self.price_change['Approval_or_rejection_time'],
            "price_change_created_time": self.price_change['db_fill_time'],
        }

    def extract_recipient_list(self):
        raise NotImplementedError('Subclass must override this')

    def get_mail_subject(self):
        raise NotImplementedError('Subclass must override this')

    def get_phone_msg_body(self):
        raise NotImplementedError('Subclass must override this')

    # send email notification
    def send_alarm_notification(self):
        mail_recipients = self.extract_recipient_list()
        msg_subject = self.get_mail_subject()

        if len(mail_recipients) > 0:
            for each in mail_recipients:
                self.context["full_username"] = each['Name']
                emailmsg = loader.render_to_string(self.email_template_name, self.context)
                msg = requests.post(
                    config("MAIL_BASE_URL"), 
                    auth=("api", 
                    config("MAILGUN_SECRET_KEY")), 
                    data = {"from": config("MAIL_SENDER"), "to": [each['Email']], "subject": msg_subject, "text": emailmsg}
                )
                if msg.status_code == 200:
                    print("True")
    
    def save_data_to_db(self):
        msg_context = self.context
        title = self.get_mail_subject()
        message = self.get_phone_msg_body(msg_context['approver'], msg_context['price'],msg_context['Initiator'],  msg_context['created_time'])
        status = 'Unread'
        message_recipients = self.extract_recipient_list()
        if len(message_recipients) > 0:
            for each in message_recipients:
                user_obj = models.User.objects.get(pk=each['id'])
                try:
                    models.Notifications.objects.create(title=title,message=message,status=status,user=user_obj)
                except:
                    # log to file
                    print("i did not save")

    # send phone message notification
    def send_phone_notification(self):
        msg_context = self.context
        msg_recipients = self.extract_recipient_list()
        msg_subject = self.get_mail_subject()

        if len(msg_recipients) > 0:
            for each in msg_recipients:
                self.context["full_username"] = each['Name']
                # send msg through twilio
                message = client.messages.create(
                    body=self.get_phone_msg_body(msg_context['approver'], msg_context['price'],msg_context['Initiator'],  msg_context['created_time']),
                    from_='Escrow Trust',
                    to=''
                )

    # send push notification mobile
    def send_push_notification(self):
        msg_content = self.context
        push_notification_recipients = self.extract_recipient_list()
        msg_subject = self.get_mail_subject()
        if len(push_notification_recipients) > 0:
            for each in push_notification_recipients:
                try:
                    id = each['id']
                    utils.push_pricealarm_notification(id, msg_subject)
                    print("I pushed notification")
                except:
                    # log to file
                    print("i did not push")

    def notify(self):
        self.send_alarm_notification()
        self.send_push_notification()
        self.save_data_to_db()
        # self.send_phone_notification()


class BuyerTransactionRejectionNotifier(TransactionAlarmNotifier):
    """
    Notify seller of canceled transaction.
    """
    email_template_name = 'company_price_change_rejection.html'
    email_subject = 'Transaction Request Was Canceled!'
    phone_msg_template = ''
    push_notification_msg_template = ''

    def extract_recipient_list(self):
        # get Actor details
        user_id = self.approval_request['Actor']
        user_obj = models.UserProfile.objects.get(user=user_id)
        email = user_obj.user.email
        name = user_obj.full_name
        mobile_number = user_obj.phone_number
        
        return [{'Email': email, 'Name': name, 'id': user_id, 'Phone_number': mobile_number}]

    def get_mail_subject(self):
        return f'Transaction Request Was Canceled!'

    def get_phone_msg_body(self, full_name, price, Initiator, created_time, approver, updated_time, rejection_note):
        return f' Hello {full_name},\n The transaction deal of N{price} was cancelled by {Initiator} at {updated_time} with this extra note = >{rejection_note}.'

class TransactionRejectionNotifier(TransactionAlarmNotifier):
    """
    Notifiy buyer when seller rejects transaction deal.
    """
    email_template_name = 'site_price_change_rejection.html'
    email_subject = 'Your Transaction Request Was Rejected!'
    push_notification_msg_template = ''
    
    def extract_recipient_list(self):
        # get initiator details
        user_id = self.approval_request['Initiator']
        user_obj = models.UserProfile.objects.get(user=user_id)
        email = user_obj.user.email
        name = user_obj.full_name
        mobile_number = user_obj.phone_number
        
        return [{'Email': email, 'Name': name, 'id': user_id, 'Phone_number': mobile_number}]

    def get_mail_subject(self):
        return f'Your Transaction Request Was Rejected!'

    def get_phone_msg_body(self, full_name, price, Initiator, created_time, approver, updated_time, rejection_note):
        return f' Hello {full_name},\nYour transaction request of ₦{price} was rejected by {approver} at {updated_time} with this extra note = >{rejection_note}.'

class TransactionApprovalNotifier(TransactionAlarmNotifier):
    """
    Notify initiator of approved transaction by seller
    """
    email_template_name = 'site_price_change_approval.html'
    email_subject = 'Your Transaction Request Was Approved!'
    push_notification_msg_template = ''

    def extract_recipient_list(self):
        # get initiator details
        user_id = self.approval_request['Initiator']
        user_obj = models.UserProfile.objects.get(user=user_id)
        email = user_obj.user.email
        name = user_obj.full_name
        mobile_number = user_obj.phone_number
        
        return [{'Email': email, 'Name': name, 'id': user_id, 'Phone_number': mobile_number}]

    def get_mail_subject(self):
        return f'Your Transaction Request Was Approved!'

    def get_phone_msg_body(self, full_name, price, Initiator, created_time, approver, updated_time):
        return f' Hello {full_name}, Your transaction request of ₦{price} was successfully approved by {approver} at {updated_time}.'

class TransactionRequestNotifier(TransactionAlarmNotifier):
    """
    Notify seller of pending transaction approval request by buyer.
    """
    email_template_name = 'site_price_change_request.html'
    email_subject = 'A New Transaction Request Requires Your Action!'
    
    def extract_recipient_list(self):
        # get Actor details
        user_id = self.approval_request['Actor']
        user_obj = models.UserProfile.objects.get(user=user_id)
        email = user_obj.user.email
        name = user_obj.full_name
        mobile_number = user_obj.phone_number
        
        return [{'Email': email, 'Name': name, 'id': user_id, 'Phone_number': mobile_number}]
    
    def get_mail_subject(self):
        name = (models.UserProfile.objects.get(
            user=self.approval_request['Initiator'])).full_name
        return f'A Transaction Request Approval from {name} Requires Your Action!'

     #full_name, price, product_name, site_name, sheduled_time, Initiator, price_change_created_time, company_name, approver, updated_time, rejection_note

    def get_phone_msg_body(self, full_name, price, Initiator, created_time, approver, updated_time):
        return f'Hello {full_name}, A new transaction request of ₦{price}  needs your approval. Please note that this request was initiated by {Initiator} at  {created_time}.'

class NotificationAlarmFactory:
    # designation Buyer/Seller        
    def __init__(self, approval_request, designation, status):
        self.approval_request = approval_request
        self.designation = designation
        self.status = status

    def create_alarm_notifier(self):
        # 1.Buyer Rejection Notifier
        # 2.Buyer Transaction Request Approval
        # 3.Seller Approval Notifier
        # 4.Seller Rejection Notifier
        if self.approval_request['buyer_approval'] == True and self.designation == "Buyer":
            return TransactionRequestNotifier(self.approval_request)
        elif self.approval_request['buyer_approval'] == False and self.designation == "Buyer":
            return BuyerTransactionRejectionNotifier(self.approval_request)
        elif self.approval_request['seller_approval'] == True and self.designation == "Seller":
            return TransactionApprovalNotifier(self.approval_request)
        elif self.approval_request['seller_approval'] == False and self.designation == "Seller":
            return TransactionRejectionNotifier(self.approval_request)

"""
Task: Modidy the extract_recipient_list() method to get Actor from `seller_id`
"""