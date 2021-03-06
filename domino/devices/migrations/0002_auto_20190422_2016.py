# Generated by Django 2.1.7 on 2019-04-22 20:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='department',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='device',
            name='description',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='device',
            name='group',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='devices.Group'),
        ),
        migrations.AlterField(
            model_name='device',
            name='hostname',
            field=models.CharField(blank=True, max_length=63),
        ),
        migrations.AlterField(
            model_name='device',
            name='location',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='device',
            name='mac_address',
            field=models.CharField(blank=True, max_length=17),
        ),
        migrations.AlterField(
            model_name='device',
            name='owner',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='device',
            name='state',
            field=models.CharField(max_length=64),
        ),
    ]
