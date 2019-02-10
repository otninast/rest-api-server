# Generated by Django 2.0.2 on 2019-01-23 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api_app', '0017_auto_20190106_2153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingprogram',
            name='self_assessment_score',
            field=models.FloatField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=3, verbose_name='Your Training Score'),
        ),
    ]