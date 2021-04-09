from itertools import compress
import logging
from multiprocessing import Pool, cpu_count
import socket
import os

from django import db
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apscheduler.schedulers.background import BackgroundScheduler

from .models import Group, CleanedEmails, UnSubscribedEmails
from .services import CleaningService
from .cron import cleaning_job, mailing_job
from .utils import get_this_week

logging.basicConfig(filename=f'logs/views {get_this_week()}', filemode='a', format=f"{timezone.now()} %(message)s",
                    level='DEBUG')


class CleaningServiceView(APIView):
    def _bulk_creator(self, emails, vendor_id, default_batch_size=100):
        """
        MySQL has upper limits on batch creation (think other DBs do too I think), so chunk up to 100 and do it
        The emails come here as a result of itertools.compress on the boolean list(In case needed to change).
        """
        for _slice in range(0, len(emails), default_batch_size):
            CleanedEmails.objects.bulk_create(
                [CleanedEmails(email=i, vendor_id=vendor_id) for i in emails[_slice: _slice + default_batch_size]])

    def get(self, request):
        """
        Steps being taken ATM:
        -> Get emails for vendor in state 2
        -> Filter out emails from unsub list
        -> Spawn (4) process, and assign cleaning process to each
        -> Collect the result of list of booleans, and create cleaned emails accordingly
        """
        vendor_id = request.GET.get('vendor_id')
        vendor = Group.objects.get(id=vendor_id)
        if vendor:
            emails = vendor.get_emails_for_vendor()
            filtered_emails = set(emails).difference(UnSubscribedEmails.get_all_unsubscribed())
            host_name = socket.gethostname()

            pool = Pool(processes=cpu_count())
            db.connections.close_all()
            result_set = pool.starmap_async(CleaningService.cleaner, [(vendor_id, email, host_name, process_num)
                                                                      for process_num, email in enumerate(filtered_emails, 1)])
            result = result_set.get()
            logging.info(f"CLEANING UPDATE: Total {result.count(True)} emails added to CleanedDB")
            # self._bulk_creator(emails=list(compress(emails, result)), vendor_id=vendor_id)
            vendor.cleaned = vendor.STATUS_CLEANED
            vendor.cleaned_count = sum([i for i in result if i])
            vendor.save()
        return Response({'success': True}, status=status.HTTP_200_OK)


class Startup(APIView):
    def get(self, request):
        """
        Spawning the two crons, based on "start" command config on server.
        Set at 15 min or value from env
        """
        CRON_DELAY = int(os.environ.get('delay', 15))*60
        scheduler = BackgroundScheduler()
        scheduler.add_job(cleaning_job, 'interval', seconds=CRON_DELAY, max_instances=1)
        scheduler.add_job(mailing_job, 'interval', seconds=CRON_DELAY, max_instances=1)
        try:
            scheduler.start()
        except Exception as e:
            logging.error(f"STARTUP ERROR: {e}")
        return Response({'success': True}, status=status.HTTP_200_OK)
