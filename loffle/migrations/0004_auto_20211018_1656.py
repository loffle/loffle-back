# Generated by Django 3.2.6 on 2021-10-18 07:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loffle', '0003_raffleapply'),
    ]

    operations = [
        migrations.RenameField(
            model_name='raffle',
            old_name='finish_at',
            new_name='end_date_time',
        ),
        migrations.RenameField(
            model_name='raffle',
            old_name='begin_at',
            new_name='start_date_time',
        ),
    ]