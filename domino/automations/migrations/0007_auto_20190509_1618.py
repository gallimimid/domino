# Generated by Django 2.1.7 on 2019-05-09 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automations', '0006_auto_20190509_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='automation',
            name='next',
            field=models.ManyToManyField(to='automations.Automation'),
        ),
    ]
