import logging
import requests

from django.utils import timezone

from .models import MessageBody, Group
from .services import EmailSender
from .utils import get_this_week


logging.basicConfig(filename=f'logs/cron {get_this_week()}', filemode='a',
                    format=f"{timezone.now()} USER_LOGGING_CRON %(message)s", level='INFO')


def mailing_job():
    template = MessageBody.get_earliest_template()
    if template:
        logging.info(f"MAILING UPDATE: Job Invoked at {timezone.now()} of {template.id}")
        email_sender = EmailSender()
        email_sender.prepare_email_for_template(template_id=template.id)


def cleaning_job():
    vendor = Group.get_uncleaned_vendor()
    if vendor:
        logging.info(f"CLEANING UPDATE: Job invoked at {timezone.now()} for {vendor.id}")
        headers = {'Host': '127.0.0.1', 'Accept': '*/*'}
        requests.get(f"http://127.0.0.1:8000/clean/?vendor_id={vendor.id}", headers=headers)
