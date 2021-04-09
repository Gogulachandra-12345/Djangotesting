import logging
import smtplib
import socket
import urllib.request

from django import db
from django.core.mail import EmailMultiAlternatives, get_connection
from django.dispatch.dispatcher import receiver
from django.conf import settings
from django.utils import timezone
from django_amazon_ses import pre_send, post_send

import boto3
import dns.resolver

import django
django.setup()

from .models import MessageBody, UnSubscribedEmails, CleanedEmails
from . import MIME_types
from .utils import logging_config

MX_records = {
    'gmail.com': 'gmail-smtp-in.l.google.com',
    'yahoo.com': 'mta6.am0.yahoodns.net',
    'protonmail.com': 'mail.protonmail.ch',
    'icloud.com': 'mx01.mail.icloud.com',
    'mail.yandex.com': 'mx.yandex.ru'
}

for logger in ['boto3', 'botocore', 'urllib3']:
    logging.getLogger(logger).setLevel(logging.WARNING)
# logging.basicConfig(filename=f'log_services.txt', filemode='a', format=f"{timezone.now()} %(message)s",
#                     level='DEBUG')
logging_config('services')


class EmailSender:
    def __init__(self):
        self.conn = boto3.client('ses', region_name=settings.AWS_DEFAULT_REGION)
        self.host = socket.gethostname()
        self.RECEIVER_CHUNK_SIZE = 50

    @staticmethod
    def unsubscribe_message(email_address):
        """
        The unsubscribe message added to end of mail
        """
        return f'TO UNSUBSCRIBE FROM FUTURE EMAILS OR TO UPDATE YOUR EMAIL PREFERENCES ' \
               f'<a href="https://mybenchlist.com/unsubscribe?email={email_address}">CLICK HERE</a>'

    def prepare_email_for_template(self, template_id):
        template = MessageBody.objects.get(id=template_id)
        if template:
            recipients = template.get_emails_for_template()
            subject = template.email_subject
            sender_name = template.sender_name or settings.SENDER_NAME
            sender_email = settings.SENDER_EMAIL
            sender = f"{sender_name} <{sender_email}>"
            reply_to = [template.sender_email]
            receivers = recipients
            html_message = template.email_body
            attachments = [Attachment(att) for att in template.email_attachment.split(',')]

            quota = self.conn.get_send_quota()
            template_total_emails = template.get_emails_count_for_template()
            if quota["SentLast24Hours"] + template_total_emails > quota["Max24HourSend"]:
                template.status = template.STATUS_DELAYED
                template.status_message = "DAILY QUOTA EXCEEDED"
                logging.error(f"MAILING UPDATE: Daily Limit Reached")
            elif len(recipients) == 0:
                # Not sure if this can happen, just to be sure
                template.status = template.STATUS_DELAYED
                logging.error(f"MAILING UPDATE: Mails are not cleaned yet")
            else:
                receivers = set(receivers).difference(UnSubscribedEmails.get_all_unsubscribed())
                
                # Write this two lines better
                mail_att = [(attachment.filename, attachment.content, attachment.mime_type,) for attachment in
                            attachments if attachment.valid]
                if mail_att:
                    attachments_size = Attachment.size_check(attachments=attachments, body_len=len(html_message))
                    mail_att = mail_att if attachments_size < 10 else []
                    logging.info(f"MAILING UPDATE: TOTAL SIZE: {attachments_size}")
                    
                # Using the custom mail_sender method to format attachment and send it
                emails_sent = [
                    self.mail_sender(subject=subject, sender=sender, message_html=html_message, message_text="",
                                     email_receiver=email_receiver, mail_att=mail_att, reply_to=reply_to) for
                    email_receiver in receivers]
                logging.info(f"{emails_sent}")
                logging.info(f"MAILING UPDATE: Total {sum(emails_sent)} sent")
                template.total_sent = sum(emails_sent)
                
                # Close existing connections
                db.connections.close_all()
                template.status = template.STATUS_SUCCESS
                template.dated = timezone.now()
                template.save()

    @staticmethod
    def mail_sender(subject, sender, email_receiver, message_text, message_html, mail_att, reply_to):
        """
        Currently taking one attachment and will attach. If EmailMessage(django.core.mail) is used, there's going
        to be "Unbalanced quoted string" error. If multiple attachments : Use multiple Attachment objects and pass
        as args

        Even though I am taking care of attachment MIME type, here I am not considering the actions to take if
        attachment is of invalid type, and am sending email without attachment
        :type subject: str
        :param sender: {name} <email>
        :param email_receiver: str
        :param message_text: most probably empty string
        :param message_html: the body in HTML format
        :type mail_att: [Tuple(att.filename, att.content, att.mime_type)]
        :param reply_to: list[str] -> email address of {name email}
        """
        connection = get_connection(fail_silently=False)

        mail = EmailMultiAlternatives(subject=subject, from_email=sender, to=[email_receiver], body=message_text,
                                      connection=connection, attachments=mail_att, reply_to=reply_to)
        mail.attach_alternative(message_html + EmailSender.unsubscribe_message(email_receiver),
                                MIME_types.mime_types["htm"])
        return mail.send()

    # @receiver(pre_send)
    # def clean_email_list(self, **kwargs):
    #     pass

    # @staticmethod
    # @receiver(post_send)
    # def log_email_sent(sender, message=None, message_id=None, **kwargs):
    #     logging.info(f"MAILING UPDATE: DONE: Email sent {message_id}")


class CleaningService:
    @staticmethod
    def cleaner(vendor_id, email_address, host_name, process_num) -> bool:
        if process_num % 300 == 0:
            logging.info(f"CLEANING UPDATE: {process_num} emails for vendor {vendor_id} have been done!")
        try:
            domain = email_address.split('@')[1]
            mx_domain = str(sorted([(_.exchange, _.preference) for _ in dns.resolver.resolve(domain, 'MX')],
                                   key=lambda x: x[1])[0][0]) if (domain not in MX_records.keys()) else MX_records[domain]
            server = smtplib.SMTP()
            server.set_debuglevel(1)
            server.connect(mx_domain)
            server.helo(host_name)
            server.mail(sender='me@domain.com')
            code, message = server.rcpt(email_address)
            server.quit()

            if code == 250:
                db.connections.close_all()
                CleanedEmails.create(email_address=email_address, vendor_id=vendor_id)
                return True
        except dns.resolver.NoAnswer:
            logging.info(f"CLEANING UPDATE: Domain of email address {email_address} not found")
            return False
        except Exception as e:
            logging.error(f"Exception caught: {e}")
            return False
        else:
            return False


class Attachment:
    def __init__(self, attachment_uri):
        self.valid = False
        if attachment_uri:
            file_response = urllib.request.urlopen(url=attachment_uri)
            if file_response.status == 200:
                attachment_type = file_response.headers.get('Content-Type')
                if attachment_type in MIME_types.mime_types.values():
                    self.mime_type = attachment_type
                    self.content = file_response.read()
                    self.filename = attachment_uri.split("/")[-1]
                    self.content_size = int(len(self.content) / 1024 / 1024)
                    self.valid = self.content_size < 10
                    logging.info(
                        f"MAILING UPDATE : FILE :{self.filename} - {len(self.content) / 1024 / 1024} MB and {self.mime_type}")
                else:
                    logging.info(
                        f"MAILING UPDATE : Unsupported FILE: {attachment_uri.split('/')[-1]} - {attachment_type}")
            else:
                logging.error(f"MAILING ERROR: FETCHING FILE ERROR: {attachment_uri} with code {file_response.status}")

    @classmethod
    def size_check(cls, attachments, body_len):
        return sum([_.content_size for _ in attachments])+body_len
