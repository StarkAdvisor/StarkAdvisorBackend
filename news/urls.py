from django.urls import path
from .views import get_news, get_sources

urlpatterns = [
    path("news/sources/", get_sources, name="get-sources"),
    path("news/", get_news, name="get-news"),
]