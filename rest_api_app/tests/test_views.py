import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth.models import User
from rest_api_app.models import (TrainingProgram, MenuName,
                                 TrainingMenu, ResultTime, LapTime)


class TestUserList(TestCase):
    def setUp(self):
        self.user = User.objects.create(
                            username='testname',
                            password='19910808seki'
                            )

    def test_get(self):
        client = APIClient()
        res = client.get(reverse('user-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def tearDown(self):
        pass


class TestDataInput(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='testname', password='19910808seki')
        MenuName.objects.create(menu_name='menu')

    def test_post_invalid_data(self):
        self.training_program = {'training_image': None}
        self.training_menu = {}
        self.result_time = {}
        self.lap_time = {}

        client = APIClient()
        client.force_login(user=self.user)
        url = reverse('datainput')
        data = {'trainingData': self.training_program,
                'menuData': self.training_menu,
                'resultTime': self.result_time,
                'lapTime': self.lap_time}
        res = client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_valid_data(self):
        self.training_program = {'training_date': '2019-01-29',
                                 'daily_reflection': None,
                                 'self_assessment_score': 3,
                                 'training_image': None}

        self.training_menu = {'menu_name': 'menu',
                              'distance': 100,
                              'style': 'Fr',
                              'time_circle': 90,
                              'how_many_times': 3}

        self.result_time = [{'num_of_order': 1, 'result_time_str': '010390', 'result_time': None,
                             'lapTime': [{'num_of_order': 1, 'num_of_lap': 1, 'lap_time': '003000'}]},
                            {'num_of_order': 2, 'result_time_str': '010450', 'result_time': None,
                                'lapTime': [{'num_of_order': 2, 'num_of_lap': 1, 'lap_time': '003000'}]},
                            {'num_of_order': 3, 'result_time_str': '010560', 'result_time': None,
                                'lapTime': [{'num_of_order': 3, 'num_of_lap': 1, 'lap_time': '003000'}]}]

        client = APIClient()
        client.force_login(user=self.user)
        url = reverse('datainput')
        data = {'trainingData': self.training_program,
                'menuData': self.training_menu,
                'resultTime': self.result_time}

        res = client.post(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
