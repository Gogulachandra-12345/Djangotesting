from django.db import models


class Group(models.Model):  # Vendor
    STATUS_DEFAULT = 1
    STATUS_SCHEDULED = 2
    STATUS_CLEANED = 3

    employer_id = models.IntegerField(blank=True, null=True)
    company_id = models.IntegerField(blank=True, null=True)
    data_name = models.CharField(max_length=255, blank=True, null=True)
    count = models.IntegerField()
    cleaned = models.IntegerField(blank=True, null=True)
    dated = models.DateTimeField()
    cleaned_count = models.IntegerField(default=1, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_vendors'

    @classmethod
    def get_uncleaned_vendor(cls):
        return cls.objects.filter(cleaned=cls.STATUS_SCHEDULED).order_by('dated').first()

    def get_emails_for_vendor(self):
        return Member.objects.filter(vendor_id=self.id).values_list('email', flat=True)


class MessageBody(models.Model):  # Schedulers
    STATUS_FRESH = '1'
    STATUS_SUCCESS = '2'
    STATUS_DELAYED = '3'
    STATUS_FAILED = '4'

    vendor_id = models.IntegerField(blank=True, null=True)
    email_subject = models.TextField(blank=True, null=True)
    email_body = models.TextField(blank=True, null=True)
    schedule_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, default=STATUS_FRESH)
    employer_id = models.IntegerField(blank=True, null=True)
    company_id = models.IntegerField(blank=True, null=True)
    updated_on = models.DateTimeField()
    total_sent = models.IntegerField(help_text="Total emails sent successfully", null=True)
    unsubscribed_count = models.IntegerField(help_text="A counter of total unsubscribed emails found", null=True)
    email_attachment = models.CharField(max_length=255, null=True)
    sender_email = models.CharField(max_length=255, null=True)
    sender_name = models.CharField(max_length=255, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_vendor_schedulers'

    @classmethod
    def get_info_for_group(cls, group_id):
        return cls.objects.filter(vendor_id=group_id).first()

    @classmethod
    def get_earliest_template(cls):
        """
        Return the earliest template in Cleaned state. i.e The cleaning cron has completed
        """
        return cls.objects.filter(status__in=[cls.STATUS_FRESH, cls.STATUS_DELAYED]).order_by('schedule_date').first()

    def get_emails_for_template(self):
        return CleanedEmails.objects.filter(vendor_id=self.vendor_id).values_list('email', flat=True)

    def get_emails_count_for_template(self):
        return len(self.get_emails_for_template())


class Member(models.Model):    # Emails
    vendor_id = models.IntegerField(blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    dated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbl_vendors_data'


class CleanedEmails(models.Model):
    email = models.CharField(null=True, max_length=255)
    vendor_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "tbl_vendors_cleaned"

    @classmethod
    def create(cls, email_address, vendor_id):
        cls.objects.create(email=email_address, vendor_id=vendor_id)


class UnSubscribedEmails(models.Model):
    unsubscribed = models.CharField(max_length=255, blank=True, null=True)
    dated = models.DateTimeField()

    class Meta:
        db_table = "tbl_vendors_data_unsubscribed"

    @classmethod
    def get_all_unsubscribed(cls):
        return UnSubscribedEmails.objects.values_list('unsubscribed', flat=True)
