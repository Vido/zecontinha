from django.db import migrations, models

def postgres_forward(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    cmd_list = [
    """
        ALTER TABLE dashboard_pairstats
        ALTER COLUMN beta_rotation
        TYPE jsonb
        USING to_jsonb(beta_rotation);
    """,
    """
        ALTER TABLE dashboard_quotes
        ALTER COLUMN hquotes
        TYPE jsonb
        USING to_jsonb(hquotes);
    """,
    """
        ALTER TABLE dashboard_quotes
        ALTER COLUMN htimestamps
        TYPE jsonb
        USING to_jsonb(htimestamps);
    """,
    ]

    for sql in cmd_list:
        schema_editor.execute(sql)

def reverse_postgres(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    cmd_list = [
    """
        ALTER TABLE dashboard_pairstats
        ALTER COLUMN beta_rotation
        TYPE double precision[]
        USING beta_rotation::double precision[];
    """,
    """
        ALTER TABLE dashboard_quotes
        ALTER COLUMN hquotes
        TYPE double precision[]
        USING hquotes::double precision[];
    """,
    """
        ALTER TABLE dashboard_quotes
        ALTER COLUMN htimestamps
        TYPE date[]
        USING htimestamps::date[];
    """,
    ]

    for reverse_sql in cmd_list:
        schema_editor.execute(reverse_sql)


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0015_remove_pairstats_success'),
    ]

    operations = [
        migrations.RunPython(postgres_forward, reverse_postgres),
        migrations.AlterField(
            model_name='pairstats',
            name='beta_rotation',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='quotes',
            name='hquotes',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='quotes',
            name='htimestamps',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
