# Generated by Django 2.0 on 2019-08-10 22:40

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_auto_20190810_2034'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quotes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('market', models.CharField(choices=[('N/A', 'N/A'), ('BOVESPA', 'B3 Ações'), ('COINBASE', 'Coinbase (Crypo)')], default='N/A', max_length=32)),
                ('ticker', models.CharField(max_length=32)),
                ('hquotes', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, size=None)),
            ],
        ),
    ]
