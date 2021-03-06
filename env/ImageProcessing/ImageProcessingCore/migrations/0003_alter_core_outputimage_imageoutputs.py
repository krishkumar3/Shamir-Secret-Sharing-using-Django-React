# Generated by Django 4.0.4 on 2022-04-25 18:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ImageProcessingCore', '0002_alter_core_cipher_alter_core_finaloutput_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='core',
            name='outputImage',
            field=models.ImageField(default='frontend/src/default.jpg', upload_to='outputs/'),
        ),
        migrations.CreateModel(
            name='ImageOutputs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shares', models.ImageField(upload_to='outputs/')),
                ('un', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ImageProcessingCore.core')),
            ],
        ),
    ]
