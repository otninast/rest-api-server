# Generated by Django 2.0.2 on 2019-02-07 07:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api_app', '0023_auto_20190207_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingmenu',
            name='training_program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trainingmenus', to='rest_api_app.TrainingProgram'),
        ),
    ]