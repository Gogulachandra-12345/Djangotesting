# Generated by Django 3.0.8 on 2020-08-10 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CleanedEmails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=255, null=True)),
                ('vendor_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tbl_vendors_cleaned',
            },
        ),
        migrations.CreateModel(
            name='UnSubscribedEmails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unsubscribed', models.CharField(blank=True, max_length=255, null=True)),
                ('dated', models.DateTimeField()),
            ],
            options={
                'db_table': 'tbl_vendors_data_unsubscribed',
            },
        ),
    ]