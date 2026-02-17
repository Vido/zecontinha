from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0015_remove_pairstats_success'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE dashboard_pairstats
                ALTER COLUMN beta_rotation
                TYPE jsonb
                USING to_jsonb(beta_rotation);
            """,
            reverse_sql="""
                ALTER TABLE dashboard_pairstats
                ALTER COLUMN beta_rotation
                TYPE double precision[]
                USING beta_rotation::double precision[];
            """,
        ),
        migrations.RunSQL(
            sql="""
                ALTER TABLE dashboard_quotes
                ALTER COLUMN hquotes
                TYPE jsonb
                USING to_jsonb(hquotes);
            """,
            reverse_sql="""
                ALTER TABLE dashboard_quotes
                ALTER COLUMN hquotes
                TYPE double precision[]
                USING hquotes::double precision[];
            """,
        ),
        migrations.RunSQL(
            sql="""
                ALTER TABLE dashboard_quotes
                ALTER COLUMN htimestamps
                TYPE jsonb
                USING to_jsonb(htimestamps);
            """,
            reverse_sql="""
                ALTER TABLE dashboard_quotes
                ALTER COLUMN htimestamps
                TYPE date[]
                USING htimestamps::date[];
            """,
        ),
    ]
