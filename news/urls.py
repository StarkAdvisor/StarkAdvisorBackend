from django.urls import path
from .views import NewsView, SourcesView

urlpatterns = [
    path("news/sources/",SourcesView.as_view(), name="get-sources"), 
    path("news/",NewsView.as_view() , name="get-news"),
]