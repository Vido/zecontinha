from django.db import migrations, models

def postgres_forward(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    sql="""
        ALTER TABLE backtest_pairstats
        ALTER COLUMN beta_rotation
        TYPE jsonb
        USING to_jsonb(beta_rotation);
    """
    schema_editor.execute(sql)

def reverse_postgres(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    reverse_sql="""
        ALTER TABLE backtest_pairstats
        ALTER COLUMN beta_rotation
        TYPE double precision[]
        USING beta_rotation::double precision[];
    """
    schema_editor.execute(reverse_sql)


class Migration(migrations.Migration):

    dependencies = [
        ('backtest', '0004_remove_pairstats_success'),
    ]

    operations = [
        migrations.RunPython(postgres_forward, reverse_postgres),
        migrations.AlterField(
            model_name='pairstats',
            name='beta_rotation',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
