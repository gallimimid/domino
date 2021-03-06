# Generated by Django 2.1.7 on 2019-04-22 19:17

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devices.Device')),
            ],
            options={
                'ordering': ['-time_stamp'],
            },
        ),
        migrations.CreateModel(
            name='EventDefinition',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('message', models.CharField(max_length=256)),
                ('severity', models.CharField(choices=[('C', 'CRITICAL'), ('W', 'Warning'), ('I', 'information')], max_length=1)),
                ('condition', models.CharField(choices=[('&&', 'All'), ('||', 'Any')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Measure',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
                ('key', models.CharField(max_length=128)),
                ('value', models.CharField(max_length=128)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devices.Device')),
            ],
            options={
                'ordering': ['-time_stamp'],
            },
        ),
        migrations.CreateModel(
            name='Trigger',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('key', models.CharField(max_length=128)),
                ('operator', models.CharField(choices=[('==', 'equal to'), ('!=', 'not equal to'), ('>', 'greater than'), ('<', 'less than'), ('>=', 'greater than or equal to'), ('<=', 'less than or equal to'), ('.*', 'contains'), ('!*', 'does not contain'), ('^*', 'starts with'), ('*$', 'ends with')], max_length=3)),
                ('value', models.CharField(max_length=128)),
                ('hysteresis', models.DurationField()),
                ('event_definition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.EventDefinition')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='event_definition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.EventDefinition'),
        ),
    ]
