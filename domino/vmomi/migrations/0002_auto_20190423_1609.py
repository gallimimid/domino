# Generated by Django 2.1.7 on 2019-04-23 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vmomi', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vmomiconfig',
            name='session_key',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]