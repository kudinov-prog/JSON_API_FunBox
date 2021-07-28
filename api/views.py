import time
import redis

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


redis_instance = redis.Redis(host='localhost', port=6379, db=0)


class PostVisitsView(APIView):

    def post(self, request):
        current_timestamp = int(time.time())

        if 'links' not in request.data:
            response = {'status': 'JSON must have "links" key'}

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        links_list = request.POST.getlist('links') or request.data['links']

        if not all(isinstance(item, str) for item in links_list):
            response = {'status': 'All links must be strings'}

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        redis_instance.sadd(current_timestamp, *links_list)

        response = {'status': 'ok'}

        return Response(response, status=status.HTTP_201_CREATED)

