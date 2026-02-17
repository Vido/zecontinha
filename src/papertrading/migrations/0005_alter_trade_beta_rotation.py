from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('papertrading', '0004_auto_20231130_1558'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE papertrading_trade
                ALTER COLUMN beta_rotation
                TYPE jsonb
                USING to_jsonb(beta_rotation);
            """,
            reverse_sql="""
                ALTER TABLE papertrading_trade
                ALTER COLUMN beta_rotation
                TYPE double precision[]
                USING beta_rotation::double precision[];
            """,
        ),
    ]
