# Generated by Django 4.0.4 on 2022-06-04 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ImageProcessingCore', '0014_userimagelist'),
    ]

    operations = [
        migrations.AddField(
            model_name='userimagelist',
            name='fromemail',
            field=models.EmailField(default='', max_length=254),
        ),
    ]
