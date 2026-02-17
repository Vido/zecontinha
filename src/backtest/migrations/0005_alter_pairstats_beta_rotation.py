from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backtest', '0004_remove_pairstats_success'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE backtest_pairstats
                ALTER COLUMN beta_rotation
                TYPE jsonb
                USING to_jsonb(beta_rotation);
            """,
            reverse_sql="""
                ALTER TABLE backtest_pairstats
                ALTER COLUMN beta_rotation
                TYPE double precision[]
                USING beta_rotation::double precision[];
            """,
        ),
    ]
