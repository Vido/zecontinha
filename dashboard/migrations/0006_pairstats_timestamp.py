# Generated by Django 2.0 on 2019-08-08 14:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_auto_20190807_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='pairstats',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
