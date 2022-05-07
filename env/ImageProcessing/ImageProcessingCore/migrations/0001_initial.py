# Generated by Django 4.0.4 on 2022-04-18 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Core',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n', models.IntegerField()),
                ('k', models.IntegerField()),
                ('inputImage', models.ImageField(upload_to='uploads/')),
                ('outputImage', models.ImageField(upload_to='downloads/')),
                ('cipher', models.TextField()),
                ('finalOutput', models.TextField()),
            ],
        ),
    ]