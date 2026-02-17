from django.db import migrations, models

def postgres_forward(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    sql="""
        ALTER TABLE papertrading_trade
        ALTER COLUMN beta_rotation
        TYPE jsonb
        USING to_jsonb(beta_rotation);
    """
    schema_editor.execute(sql)

def reverse_postgres(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    reverse_sql="""
        ALTER TABLE papertrading_trade
        ALTER COLUMN beta_rotation
        TYPE double precision[]
        USING beta_rotation::double precision[];
    """
    schema_editor.execute(reverse_sql)


class Migration(migrations.Migration):

    dependencies = [
        ('papertrading', '0004_auto_20231130_1558'),
    ]
    migrations.RunPython(postgres_forward, reverse_postgres),
    operations = [
        migrations.AlterField(
            model_name='trade',
            name='beta_rotation',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]

