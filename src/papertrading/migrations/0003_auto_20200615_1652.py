import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('papertrading', '0002_auto_20200612_2135'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='periodo',
            field=models.IntegerField(choices=[], default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='trade',
            name='beta_rotation',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='trade',
            name='market',
            field=models.CharField(choices=[('N/A', 'N/A'), ('BOVESPA', 'B3 Ações'), ('COINBASE', 'Coinbase (Crypo)')], default='N/A', max_length=32),
        ),
        migrations.AlterField(
            model_name='trade',
            name='model_params',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]
