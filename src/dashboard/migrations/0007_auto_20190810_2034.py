import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_pairstats_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='pairstats',
            name='beta_rotation',
            # field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, default=[], size=None),
            field=models.JSONField(blank=True, default=list),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trade',
            name='beta_rotation',
            # field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, default=[], size=None),
            field=models.JSONField(blank=True, default=list),
            preserve_default=False,
        ),
    ]
