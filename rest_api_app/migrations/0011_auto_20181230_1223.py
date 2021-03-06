# Generated by Django 2.0.2 on 2018-12-30 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api_app', '0010_auto_20181229_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(upload_to='image', verbose_name='Profile Image'),
        ),
        migrations.AlterField(
            model_name='trainingprogram',
            name='training_image',
            field=models.ImageField(null=True, upload_to='image', verbose_name='Training Image'),
        ),
    ]
