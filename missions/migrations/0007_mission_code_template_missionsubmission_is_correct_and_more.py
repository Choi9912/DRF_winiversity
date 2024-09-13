# Generated by Django 5.1.1 on 2024-09-13 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('missions', '0006_alter_mission_correct_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='code_template',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='missionsubmission',
            name='is_correct',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='missionsubmission',
            name='submitted_code',
            field=models.TextField(blank=True, null=True),
        ),
    ]
