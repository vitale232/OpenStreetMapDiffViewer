# Generated by Django 2.2.1 on 2019-07-18 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osm_sniffer', '0011_auto_20190718_0802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='milepointroute',
            name='roadway_signing',
            field=models.IntegerField(choices=[(1, 'I'), (2, 'US'), (3, 'NY'), (-9999, '')], null=True),
        ),
    ]
