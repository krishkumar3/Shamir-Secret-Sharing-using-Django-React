# Generated by Django 4.0.4 on 2022-05-07 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ImageProcessingCore', '0007_imageoutputs_cipher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageoutputs',
            name='shares',
            field=models.ImageField(upload_to='frontend/src/outputs/'),
        ),
    ]
