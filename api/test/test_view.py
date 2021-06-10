# -*- coding: utf-8 -*-
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory
from django.urls import reverse
import pytest
from api.pymongo_driver import db_driver, get_qs, update_data
from time import sleep
import requests
import json
from pytest import raises
from celery.exceptions import Retry
# for python 2: use mock.patch from `pip install mock`.
from unittest.mock import patch
from django.contrib.auth import get_user_model


class TestApi(TestCase):

    @pytest.fixture(scope='session')
    def celery_config(self):
        return {
            'broker_url': 'redis://127.0.0.1:6379/0',
            'result_backend': 'redis://127.0.0.1:6379/1'
        }

    def setUp(self):
        self.factory_client = APIRequestFactory()
        self.api_client = APIClient()
        self.api_client_unauthorized = APIClient()
        self.api_client_new = APIClient()
        self.scrap_web_url = "http://127.0.0.1:8000/api/v1/web-scrap/"
        self.get_list_url = "http://127.0.0.1:8000/api/v1/get-collection/"
        self.scrap_web_url_wrong = "http://127.0.0.1:8000/api/v2/web-scrap"
        self.token = "45375db1d21d9f099da95b7461b3be1df87f06ea"
        self.scrap_url_A = "https://cannolive.fr/huile-dolive-fruitee/110-1l-huile-d-olive-vierge-extra-fruitee.html"
        self.scrap_url_B = "https://www.gallico-fashion.com/classical-x-back/"
        self.scrap_url_C = "123xyz.com"
        self.scrap_url_D = "acd2343.com"

        # creating a user objects
        User = get_user_model()
        self.test_user = User.objects.create_superuser(username='ml@pertimm.com', password='password')
        self.test_user2 = User.objects.create_superuser(username='secondMl@pertimm.com', password="secondpassword")
        self.test_user3 = User.objects.create_user(username='third@pertimm.com', password='thirdpassword')
        # for getting a Token
        self.token = Token.objects.create(user=self.test_user)
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.api_client_new.credentials(HTTP_AUTHORIZATION= 'Token ' + "45375db1d21d9f099da95b7461b3be1df87f06ea")
        self.api_client_unauthorized.credentials(HTTP_AUTHORIZATION='Token ' + 'pqrstuvwxyw12345676645#948571245#$%#')


    def test_scrap(self):
        response = self.api_client.post(self.scrap_web_url, data={"website": self.scrap_url_A}, format="json")
        self.assertEqual(response.status_code, 200)


    # @pytest.mark.celery(result_backend='redis://redis')
    def test_scrap_wrong_url(self):
        response = self.api_client.post(self.scrap_web_url_wrong, data={"website": self.scrap_url_A}, format='json')
        self.assertEqual(response.status_code, 404)

    def test_scrap_wrong_method(self):
        response = self.api_client.get(self.scrap_web_url, kwargs={"website": self.scrap_url_A})
        self.assertEqual(response.status_code, 405)

    def test_scrap_wrong_url_wrong_method(self):
        response = self.api_client.get(
            self.scrap_web_url, kwargs={"website": self.scrap_web_url_wrong},
            format='json'
        )
        self.assertEqual(response.status_code, 405)

    def test_scrap_unauthorized(self):
        response = self.api_client_unauthorized.get(
            self.scrap_web_url, data={"website": self.scrap_url_B},
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_get_list_unauthorized(self):
        response = self.api_client_unauthorized.get(
            reverse('get_collection'), data={"get_list": self.scrap_url_A},
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_get_collection(self):
        response = self.api_client_new.get(reverse('get_collection'), data={"get_list": self.scrap_url_A},
                                       format='json')
        self.assertEqual(response.status_code, 401)

    def test_driver(self):
        test_value = None
        data = get_qs({"url":self.scrap_url_A})
        if data:
            test_value = True

        self.assertEqual(test_value, True)
        product = {
            "url": self.scrap_url_A, "title": "test_title", "categories": "test_categories",
            "price": "test_price", "images": "test_images", "description": "test_description",
            "extra": "test_extra", "currency": "test_currency"
        }

        new_data = update_data(product)
        self.assertEqual(new_data, True)
