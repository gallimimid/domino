# Generated by Django 2.1.7 on 2019-05-03 18:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0003_auto_20190422_2019'),
        ('automations', '0003_auto_20190503_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='automation',
            name='source_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='source_group', to='devices.Group'),
        ),
        migrations.AlterField(
            model_name='automation',
            name='target_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='target_group', to='devices.Group'),
        ),
    ]