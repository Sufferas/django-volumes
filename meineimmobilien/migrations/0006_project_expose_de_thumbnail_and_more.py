# Generated by Django 4.2.4 on 2024-01-10 12:21

from django.db import migrations, models
import meineimmobilien.models


class Migration(migrations.Migration):

    dependencies = [
        ('meineimmobilien', '0005_dokumentethumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='expose_de_thumbnail',
            field=models.ImageField(default=1, upload_to=meineimmobilien.models.project_directory_path_expose),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='expose_en_thumbnail',
            field=models.ImageField(default=1, upload_to=meineimmobilien.models.project_directory_path_expose),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='expose_ru_thumbnail',
            field=models.ImageField(default=1, upload_to=meineimmobilien.models.project_directory_path_expose),
            preserve_default=False,
        ),
    ]
