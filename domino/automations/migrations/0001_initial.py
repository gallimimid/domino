# Generated by Django 2.1.7 on 2019-04-22 19:17

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Automation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('effect', models.CharField(max_length=200, verbose_name='task name')),
                ('cause', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.EventDefinition')),
            ],
        ),
    ]
