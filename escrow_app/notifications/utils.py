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


class PriceAlarmNotifier:
    alarm_type = ''
    email_template_name = ''
    email_subject = ''
    mail_list = ''
    phone_msg_template = ''
    push_notification_msg_template = ''

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

    # send alarm email notification
    def send_alarm_notification(self):
        mail_recipients = self.extract_recipient_list()
        msg_subject = self.get_mail_subject()

        if len(mail_recipients) > 0:
            for each in mail_recipients:
                self.context["full_username"] = each['Name']
                emailmsg = loader.render_to_string(
                    self.email_template_name, self.context)
                msg = requests.post(
                    config("MAIL_BASE_URL"), 
                    auth=("api", 
                    config("MAILGUN_SECRET_KEY")), 
                    data = {"from": config("MAIL_SENDER"), "to": [each['Email']], "subject": msg_subject, "text": emailmsg}
                )
                if msg.status_code == 200:
                    print("True")
                # email = EmailMessage(msg_subject, emailmsg,
                #                      'support@smartflowtech.com', [each['Email']],)
                # email.content_subtype = "html"
                # email.send(fail_silently=True)
            # send data to db
    
    def save_data_to_db(self):
        msg_context = self.context
        title = self.get_mail_subject()
        message = self.get_phone_msg_body(msg_context['full_username'], msg_context['price'], msg_context['product_name'],  msg_context['site_name'],  msg_context['sheduled_time'],  msg_context['Initiator'],  msg_context['price_change_created_time'], msg_context['company_name'], msg_context['approver'], msg_context['updated_time'], msg_context['rejection_note'])
        status = 'Unread'
        # user_id = self.price_change['Initiator']
        message_recipients = self.extract_recipient_list()
        if len(message_recipients) > 0:
            for each in message_recipients:
                user_obj = models.User.objects.get(pk=each['id'])
                company= user_obj.Company
                try:
                    models.Notifications.objects.create(title=title,message=message,status=status,user=user_obj,company=company)
                except:
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
                print('msg receiver', each['Phone_number'])
                # full_username, price, product_name,  site_name,  sheduled_time,  Initiator, price_change_created_time, company_name, approver,updated_time,rejection_note
                message = client.messages.create(
                    body=self.get_phone_msg_body(
                        msg_context['full_username'], msg_context['price'], msg_context['product_name'],  msg_context['site_name'],  msg_context['sheduled_time'],  msg_context['Initiator'],  msg_context['price_change_created_time'], msg_context['company_name'], msg_context['approver'], msg_context['updated_time'], msg_context['rejection_note']),
                    from_='Smart Pump',
                    to='+2348157787640'
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
                    print("i did not push")
                # push to mobile and web
                # print('push receiver', each['id'])
                # print('push subject', msg_subject)
                # print('push_content', msg_content)

    def notify(self):
        self.send_alarm_notification()
        self.send_push_notification()
        self.save_data_to_db()
        # self.send_phone_notification()


class CompanyPriceRejectionNotifier(PriceAlarmNotifier):
    email_template_name = 'company_price_change_rejection.html'
    email_subject = 'Your Price Change Request Was Rejected!'
    phone_msg_template = ''
    push_notification_msg_template = ''

    def extract_recipient_list(self):
        # get initiator email
        user_id = self.price_change['Initiator']
        user_obj = models.User.objects.get(pk=user_id)
        email = user_obj.Email
        name = user_obj.Name
        mobile_number = user_obj.Phone_number
        return [{'Email': email, 'Name': name, 'id': user_id, 'Phone_number': mobile_number}]

    def get_mail_subject(self):
        return f'Your Price Change Request Was Rejected!'

    def get_phone_msg_body(self, full_name, price, product_name, site_name, sheduled_time, Initiator, price_change_created_time, company_name, approver, updated_time, rejection_note):
        return f' Hello {full_name},\nYour request to make a price change of N{price} for {product_name} in all sites at {company_name} was rejected by {approver} at {updated_time} with this extra note = >{rejection_note}.'

class CompanyPriceApprovalNotifier(PriceAlarmNotifier):
    email_template_name = 'company_price_change_approval.html'
    email_subject = 'Your Price Change Request Was Approved!'
    push_notification_msg_template = ''

    def extract_recipient_list(self):
        # get initiator details
        user_id = self.price_change['Initiator']
        user_obj = models.User.objects.get(pk=user_id)
        email = user_obj.Email
        name = user_obj.Name
        mobile_number = user_obj.Phone_number
        return [{'Email': email, 'Name': name, 'id': user_id, 'Phone_number': mobile_number}]

    def get_mail_subject(self):
        return f'Your Price Change Request Was Approved!'
    # full_name, price, product_name, site_name, sheduled_time, Initiator, price_change_created_time, company_name, approver, updated_time, rejection_note

    def get_phone_msg_body(self, full_name, price, product_name, site_name, sheduled_time, Initiator, price_change_created_time, company_name, approver, updated_time, rejection_note):
        return f' Hello {full_name}, \nYour request to make a price change of ₦{price} for {product_name} by {sheduled_time} at all sites in {company_name} was successfully approved by {approver} at {updated_time}.'

class SitePriceRejectionNotifier(PriceAlarmNotifier):
    email_template_name = 'site_price_change_rejection.html'
    email_subject = 'Your Price Change Request Was Rejected!'
    push_notification_msg_template = ''

    def extract_recipient_list(self):
        # get initiator details
        user_id = self.price_change['Initiator']
        user_obj = models.User.objects.get(pk=user_id)
        email = user_obj.Email
        name = user_obj.Name
        mobile_number = user_obj.Phone_number
        return [{'Email': email, 'Name': name, 'id': user_id, 'Phone_number': mobile_number}]

    def get_mail_subject(self):
        return f'Your Price Change Request Was Rejected!'

    def get_phone_msg_body(self, full_name, price, product_name, site_name, sheduled_time, Initiator, price_change_created_time, company_name, approver, updated_time, rejection_note):
        return f' Hello {full_name},\nYour request to make a price change of ₦{price} for {product_name} in {site_name} was rejected by {approver} at {updated_time} with this extra note = >{rejection_note}.'

class SitePriceApprovalNotifier(PriceAlarmNotifier):
    email_template_name = 'site_price_change_approval.html'
    email_subject = 'Your Price Change Request Was Approved!'
    push_notification_msg_template = ''

    def extract_recipient_list(self):
        # get initiator details
        user_id = self.price_change['Initiator']
        user_obj = models.User.objects.get(pk=user_id)
        email = user_obj.Email
        name = user_obj.Name

        mobile_number = user_obj.Phone_number
        return [{'Email': email, 'Name': name, 'id': user_id, 'Phone_number': mobile_number}]

    def get_mail_subject(self):
        return f'Your Price Change Request Was Approved!'

    def get_phone_msg_body(self, full_name, price, product_name, site_name, sheduled_time, Initiator, price_change_created_time, company_name, approver, updated_time, rejection_note):
        return f' Hello {full_name}, Your request to make a price change of N{price} for {product_name} in {site_name} was successfully approved by {approver} at {updated_time}.'

class SitePriceRequestNotifier(PriceAlarmNotifier):
    email_template_name = 'site_price_change_request.html'
    email_subject = 'A New Price Change at  Request Requires Your Action!'

    def extract_recipient_list(self):
        # get users with Company Admin Role and Super User Role
        company = self.price_change['Company']
        if company == 1:
            recipients = models.User.objects.filter(
                Email__in=['muhammad.salihu@smartflowtech.com','idowu.sekoni@smartflowtech.com'], is_active=True).values('Email', 'Name', 'id', 'Phone_number')
            # recipients = models.User.objects.filter(
            #     Company=company, Role__Role_id__in=[3], is_active=True).values('Email', 'Name', 'id', 'Phone_number')
        else:
            recipients = models.User.objects.filter(
                Company=company, Role__Role_id__in=[2], is_active=True).values('Email', 'Name', 'id', 'Phone_number')
        return recipients

    def get_mail_subject(self):
        site_name = (models.Sites.objects.get(
            pk=self.price_change['Site'])).Name
        return f'A New Price Change Request for {site_name} Requires Your Action!'

     #full_name, price, product_name, site_name, sheduled_time, Initiator, price_change_created_time, company_name, approver, updated_time, rejection_note

    def get_phone_msg_body(self, full_username, price, product_name,  site_name,  sheduled_time,  Initiator, price_change_created_time, company_name, approver, updated_time, rejection_note):
        return f'Hello {full_username}, A new price change request of ₦{price} for {product_name} at {site_name} needs your approval to take effect by {sheduled_time}. Please note that this request was initiated by {Initiator} at  {price_change_created_time}.'

class CompanyPriceRequestNotifier(PriceAlarmNotifier):
    email_template_name = 'company_price_change_request.html'
    email_subject = 'A New Price Change Request Requires Your Action!'
    push_notification_msg_template = ''

    def extract_recipient_list(self):
        # get users with Company Admin Role
        # Only get super admin if company is Smartflow
        company = self.price_change['Company']
        if company == 1:
            recipients = models.User.objects.filter(
                Email__in=['muhammad.salihu@smartflowtech.com','idowu.sekoni@smartflowtech.com','jamiu.adeyemi@smartflowtech.com'], is_active=True).values('Email', 'Name', 'id', 'Phone_number')

            # recipients = models.User.objects.filter(
            #     Company=company, Role__Role_id__in=[3], is_active=True).values('Email', 'Name', 'id', 'Phone_number')
        else:
            recipients = models.User.objects.filter(
                Company=company, Role__Role_id__in=[2], is_active=True).values('Email', 'Name', 'id', 'Phone_number')
        return recipients

    def get_mail_subject(self):
        company_name = (models.Companies.objects.get(
            pk=self.price_change['Company'])).Name
        return f'A New Price Change Request at {company_name} Requires Your Action!'

    # full_name, price, product_name, site_name, sheduled_time, Initiator, price_change_created_time, company_name, approver, updated_time, rejection_note

    def get_phone_msg_body(self, full_username, price, product_name,  site_name,  sheduled_time,  Initiator, price_change_created_time, company_name, approver, updated_time, rejection_note):
        return f' Hello {full_username},\nA new price change request of ₦{price} for {product_name} in all sites in  {company_name} needs your approval(or rejection) to take effect by {sheduled_time}.\nAn approval means all sites would be selling {product_name} at the rate of ₦{price}/Unit.\nPlease note that this request was initiated by {Initiator} at {price_change_created_time}.'


class NotificationAlarmFactory:
    # designation means price_change is for company or site
    def __init__(self, price_change_request, designation, is_initial_price):
        self.price_change = price_change_request
        self.designation = designation
        self.is_initial_price = is_initial_price

    def create_alarm_notifier(self):
        # 5 alarm levels exist
        # 1.Company Price Approved 2.Company Price Rejected
        # 3.Site Price Approved 4.Site Price Rejected 5. Price Change Request
        if self.price_change['Approved'] == True and self.designation == "Company":
            return CompanyPriceApprovalNotifier(self.price_change)
        elif self.price_change['Approved'] == False and self.designation == "Company":
            return CompanyPriceRejectionNotifier(self.price_change)
        elif self.price_change['Approved'] == True and self.designation == "Site":
            return SitePriceApprovalNotifier(self.price_change)
        elif self.price_change['Approved'] == False and self.designation == "Site":
            return SitePriceRejectionNotifier(self.price_change)
        elif self.is_initial_price and self.designation == "Company":
            return CompanyPriceRequestNotifier(self.price_change)
        elif self.is_initial_price and self.designation == "Site":
            return SitePriceRequestNotifier(self.price_change)
