# Generated by Django 2.2.1 on 2019-07-18 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osm_sniffer', '0009_osmdiffbuffer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='milepointroute',
            name='roadway_signing',
            field=models.IntegerField(choices=[(0, 'I'), (1, 'US'), (2, 'NY'), (-9999, '')], null=True),
        ),
    ]
