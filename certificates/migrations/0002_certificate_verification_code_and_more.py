# Generated by Django 5.1.1 on 2024-09-22 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate',
            name='verification_code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='pdf_url',
            field=models.URLField(blank=True),
        ),
    ]