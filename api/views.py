import json
from time import sleep

from bson import json_util
from celery import shared_task
from django.conf.urls import url
from rest_framework import status, permissions, authentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_swagger.views import get_swagger_view

from .gen_scrappy.main.product_crawler import start_scrap
from .pymongo_driver import db_driver, status_compelete, get_status_flag
from .util import restJsonify

schema_view = get_swagger_view(title='Pastebin API')
db = db_driver()

urlpatterns = [
    url(r'^$', schema_view)
]


# Create your views here.

@shared_task(name="scarpping_task")
def task_forward(url):
    try:
        start_scrap(url)
    except:
        return "data scrapping error"
    return True


class ScrapApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        if 'website' in data:
            url = data['website']

            task_forward.delay(url)
            print("task sent")

            response_data = {

                'websites': data['website'],
                'status': status.HTTP_200_OK
            }

            return Response(response_data, status=status.HTTP_200_OK)
        return Response("Not found", status=status.HTTP_404_NOT_FOUND)


class GetScrapApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request):
        domain = ""
        url = ""
        work_status = ""
        try:
            domain = request.query_params.get('id')
            url = domain.split('/')[2]
            work_status = get_status_flag(url)
        except:
            pass
        try:
            data_qs = db[url].find()
            # data_qs['status']= status
            data_qs = list(data_qs)
            rest_parse = restJsonify(data_qs)

            response = {"status": work_status, "data": rest_parse}
            if data_qs:
                return Response(response, status=status.HTTP_200_OK)
            return Response("There is no any collection on given data", status=status.HTTP_204_NO_CONTENT)
        except Exception as er:
            return Response(f'Not available, {er}', status=status.HTTP_404_NOT_FOUND)

        # if 'get_document' in data:
        #     url = data['get_document'].split('/')[2]
        #     url_list = []
        #     output = {
        #         'url': url_list
        #     }

        # #data_qs = db[url].find()
        # data_qs = db[url].find({"url":data['get_document']})

        # parse_data = restJsonify(list(data_qs))

        # print(parse_data)

        # list_data = list(data_qs)
        # '''
        # json_data = dumps(list_data)
        # my_data = json.loads(json_data)
        # response_data = json.dumps(my_data)
        # my_data = json.loads(response_data)
        # response_data = json.dumps(my_data)
        # '''

        # #print("the data is ", my_data)
        # with open('data.json', 'w') as file:
        #     file.write(json_data)

        # if data_qs is not None:
        #     return Response(parse_data, status=status.HTTP_200_OK)
