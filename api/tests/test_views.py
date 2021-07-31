import datetime
from django.http import response
import redis
from freezegun import freeze_time
from unittest import mock
from rest_framework.test import APITestCase, APIClient


class PostvisitsAPITests(APITestCase):
    """
    Тестирование работоспособности передачи данных Post-запросом
    """

    def setUp(self):

        self.client = APIClient()
        self.test_redis = redis.Redis(host='localhost', port=6379, db=1)

    @freeze_time(datetime.datetime.utcfromtimestamp(1627575767))
    def test_post_single_valid_link(self):
        """
        Тестирование передачи одной валидной ссылки 
        """
        data = {
            'links': [
                'https://yandex.ru?=111111'
            ]
        }

        with mock.patch('redis.Redis', return_value=self.test_redis):
            response = self.client.post('/api/visited_links', data)

        redis_data_bytes = self.test_redis.smembers('1627575767')
        redis_data_str = [x.decode('utf-8') for x in redis_data_bytes]

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('status'), 'ok')
        self.assertCountEqual(redis_data_str, data.get('links'))

        self.test_redis.flushdb()

    @freeze_time(datetime.datetime.utcfromtimestamp(1627575770))
    def test_post_valid_links(self):
        """
        Тестирование передачи нескольких валидных ссылок
        """
        data = {
            'links': [
                'https://yandex.ru?=111111',
                'vk.com',
                'redis.io'
            ]
        }

        with mock.patch('redis.Redis', return_value=self.test_redis):
            response = self.client.post('/api/visited_links', data)

        redis_data_bytes = self.test_redis.smembers('1627575770')
        redis_data_str = [x.decode('utf-8') for x in redis_data_bytes]

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('status'), 'ok')
        self.assertCountEqual(redis_data_str, data.get('links'))

        self.test_redis.flushdb()

    @freeze_time(datetime.datetime.utcfromtimestamp(1627575770))
    def test_post_invalid_links(self):
        data = {
            'avto': [
                'toyota'
            ]
        }

        with mock.patch('redis.Redis', return_value=self.test_redis):
            response = self.client.post('/api/visited_links', data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('status'), 'JSON must have "links" key')
