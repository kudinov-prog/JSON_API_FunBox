import datetime
import redis

from freezegun import freeze_time
from unittest import mock
from rest_framework.test import APITestCase, APIClient


class PostVisitsAPITests(APITestCase):
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
        self.assertEqual(
            response.data.get('status'), 'JSON must have "links" key'
        )


class GetDomainsAPITests(APITestCase):
    """
    Тестирование работоспособности получения данных GET-запросом
    """

    def setUp(self):

        self.client = APIClient()
        self.test_redis = redis.Redis(host='localhost', port=6379, db=1)

    def test_get_domains(self):
        """
        Тестирование получения списка уникальных доменов, посещенных
        за переданный интервал времени
        """

        self.test_redis.sadd(
            '1620000000', 'https://www.bookung.com' 'hhtps://music.yandex.ru'
        )
        self.test_redis.sadd('1620000150', 'https://www.instagram.com')
        self.test_redis.sadd(
            '1620000300', 'https//github.com' 'https://redis.io'
        )

        with mock.patch('redis.Redis', return_value=self.test_redis):
            response = self.client.get(
                '/api/visited_domains?from=1620000050&to=1620000400'
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('status'), 'ok')
        self.assertCountEqual(
            list(response.data.get('domains')), ['instagram.com', 'redis.io']
            )

        self.test_redis.flushdb()

    def test_get_domains_without_time_interval(self):
        """
        Тестирование получения списка уникальных доменов без переданного
        интервала времени
        """
        with mock.patch('redis.Redis', return_value=self.test_redis):
            response = self.client.get('/api/visited_domains')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data.get('status'), 'Not valid time interval'
        )

    def test_get_domains_with_invalid_intervals(self):
        """
        Тестирование получения списка уникальных доменов без переданного
        валидного интервала времени
        """
        with mock.patch('redis.Redis', return_value=self.test_redis):
            response = self.client.get(
                '/api/visited_domains?from=invalid&to=interval'
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data.get('status'), 'Not valid time interval'
        )
