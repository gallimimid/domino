# Generated by Django 2.1.7 on 2019-05-08 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0003_auto_20190422_2019'),
        ('events', '0006_auto_20190506_1935'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='device',
        ),
        migrations.AddField(
            model_name='event',
            name='device_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='devices.Group'),
        ),
    ]
