from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import (
    User,
)

import rest_api_app.utils as utils

from statistics import mean


class ImageTest(models.Model):
    image = models.ImageField(upload_to='image')


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    family_name = models.CharField(
        'Family Name', max_length=30, null=True, blank=True)
    first_name = models.CharField(
        'First Name', max_length=30, null=True, blank=True)
    birthday = models.DateField('Birthday', null=True, blank=True)
    sex = models.CharField('Sex', max_length=5,
                           choices=utils.SEX_CHOICES, null=True, blank=True)
    profile_image = models.ImageField(
        'Profile Image', upload_to='image', default='image/temp_RjtSKGy.png')
    style_one = models.CharField(
        'Style1', max_length=5, choices=utils.STYLE_CHOICES, null=True, blank=True)

    def __str__(self):
        return "{}'s profile".format(self.user)


class MenuName(models.Model):
    menu_name = models.CharField('Training Menu Name', max_length=50)

    def __str__(self):
        return self.menu_name


class TrainingProgram(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    training_date = models.DateField('Date of Training', default=timezone.now)
    daily_reflection = models.CharField(
        'Reflection for Training',
        max_length=1000, null=True, blank=True)
    self_assessment_score = models.FloatField(
        'Your Training Score', default=3)
    training_image = models.ImageField(
        'Training Image', upload_to='image', null=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.training_date, self.username)


class TrainingMenu(models.Model):
    training_program = models.ForeignKey(
                        TrainingProgram,
                        on_delete=models.CASCADE,
                        related_name='TrainingProgram')
    menu_name = models.ForeignKey(MenuName, on_delete=models.CASCADE)
    distance = models.PositiveSmallIntegerField(
                        'Distance for the Training Menu',
                        choices=utils.DISTANCE_CHOICES)
    style = models.CharField(
                        'Swim Style for the Training Menu',
                        choices=utils.STYLE_CHOICES,
                        max_length=10)
    time_circle = models.PositiveSmallIntegerField(
                        'Time Circle for the Training Menu')
    how_many_times = models.PositiveSmallIntegerField('How Meny Swim?')

    def __str__(self):
        return '{} {} {}'.format(self.training_program.username,
                                 self.training_program.training_date,
                                 self.menu_name)

    def get_result_time_list(self):
        # print('-----------------')
        result_time_instance_list = ResultTime.objects.filter(
            training_menu=self)
        result_time_list = [
            result_time_instance.result_time for result_time_instance in result_time_instance_list]
        # print(result_time_list)
        lap_time_list = [
            result_time_instance.get_lap_time_list() for result_time_instance in result_time_instance_list]
        # print(lap_time_list)
        return result_time_list, lap_time_list

    def get_mean_time(self):
        time_list, lap_list = self.get_result_time_list()
        return round(mean(time_list), 2)

    def get_max_time(self):
        time_list, lap_list = self.get_result_time_list()
        return max(time_list)

    def get_min_time(self):
        time_list, lap_list = self.get_result_time_list()
        return min(time_list)

    def make_graph(self):
        time_list, lap_list = self.get_result_time_list()

        # print(lap_list)
        b64_graph = utils.make_img(time_list, lap_list)
        return b64_graph


class ResultTime(models.Model):
    training_menu = models.ForeignKey(TrainingMenu, on_delete=models.CASCADE)
    num_of_order = models.PositiveSmallIntegerField()
    result_time = models.FloatField(null=True, default=None)

    def get_lap_time_list(self):
        lap_time_instance_list = LapTime.objects.filter(result_time=self)
        lap_time_list = [
            lap_time_instance.lap_time for lap_time_instance in lap_time_instance_list]
        return lap_time_list

    def __str__(self):
        return '{} {}'.format(self.training_menu, self.num_of_order)


class LapTime(models.Model):
    result_time = models.ForeignKey(ResultTime, on_delete=models.CASCADE)
    num_of_lap = models.PositiveSmallIntegerField()
    lap_time = models.FloatField(null=True, default=None)

    def __str__(self):
        return '{}{}'.format(self.result_time, self.num_of_lap)
