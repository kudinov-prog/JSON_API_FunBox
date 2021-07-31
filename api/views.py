import time
import redis

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


# Инициализация сервера Redis
redis_instance = redis.Redis(host='localhost', port=6379, db=0)


class PostVisitsView(APIView):
    """ Передача данных POST-запросом в формате:
        {
            "links": [
                "link1",
                "link2"
            ]
        }
    """

    def post(self, request):

        # Получение текущего времени
        current_timestamp = int(time.time())

        # Проверка на отсутсвие ключа "links" в запросе
        if 'links' not in request.data:
            response = {'status': 'JSON must have "links" key'}

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        links_list = request.POST.getlist('links') or request.data['links']

        # Проверка, что все ссылки являются строками
        if not all(isinstance(item, str) for item in links_list):
            response = {'status': 'All links must be strings'}

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Запись в хранилище redis, где ключ - время запроса,
        # значение - список ссылок
        redis_instance.sadd(current_timestamp, *links_list)

        response = {'status': 'ok'}

        return Response(response, status=status.HTTP_201_CREATED)


class GetDomainsView(APIView):
    """
    Получение GET-запросом списка уникальных доменов, посещенных в течение
    заданного интервала времени в формате:
    /visited_domains?from=<timestamp_from>&to=<timestamp_to>
    """
    def get(self, request):
        
        links_bytes_list = []
        domains_list = []

        timestamp_from = request.GET.get('from')
        timestamp_to = request.GET.get('to')

        # Проверка, что заданные значения времени являются целочисленными
        # значениями
        if (not timestamp_from or not timestamp_to or
                not timestamp_from.isdigit() or not timestamp_to.isdigit()):
            response = {'status': 'Not valid time interval'}

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        for key in redis_instance.scan_iter():
            # Проверка значения ключа на попадание в переданный интервал
            # времени
            if (not key.decode('utf-8').isdigit()
                or int(key) < int(timestamp_from)
                    or int(key) > int(timestamp_to)):
                continue

            # Если ключ имеет список значений, то они добавляются в links_set
            if redis_instance.type(key).decode('utf-8') == 'set':
                links_bytes_list.extend(redis_instance.smembers(key))

        for link in links_bytes_list:
            # Извлечение названия домена из строки и добавление в domains_list
            domains_list.append(
                (link.decode('utf-8').split('//')[-1].
                 split('www.')[-1].split('/')[0].split('?')[0])
                )

        response = {
            'domains': set(domains_list),
            'status': 'ok',
        }

        return Response(response, status=status.HTTP_200_OK)
