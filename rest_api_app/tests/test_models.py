import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from django.contrib.auth.models import User


class UserTest(TestCase):
    def test_user_post(self):
        url = reverse('user-list')
        data = {
            'username': 'testname',
            'password': '19910808seki',
        }
        res = self.client.post(url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, data['username'])
