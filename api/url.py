from django.urls import path

from .views import ScrapApiView, GetScrapApiView

urlpatterns = [
    path('v1/web-scrap/', ScrapApiView.as_view(), name='scrap'),
    path('v1/get-collection/', GetScrapApiView.as_view(), name='get_collection')
]
