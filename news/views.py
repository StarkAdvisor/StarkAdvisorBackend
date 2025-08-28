# news/views.py
from django.views import View
from django.http import JsonResponse, HttpRequest
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from news.services.news_service import NewsService

class NewsView(View):


    @staticmethod
    def _convert_objectid(data):
        if isinstance(data, list):
            for doc in data:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
        elif isinstance(data, dict):
            if "_id" in data:
                data["_id"] = str(data["_id"])
        return data

    def get(self, request: HttpRequest):
        query = request.GET.get("q", "Apple")

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        start = request.GET.get("start", str(yesterday))
        end = request.GET.get("end", str(today))
        max_articles = int(request.GET.get("max_articles", 100))
        source = request.GET.get("source")

        # Parseo de fechas
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        service =NewsService()
        data = service.fetch_news(
            category=query,
            source=source,
            start_date=start_date,
            end_date=end_date,
            limit=max_articles 
        )

        data = self._convert_objectid(data)
        return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False, "indent": 2})


class SourcesView(View):
  

    def get(self, request: HttpRequest):
        service =NewsService()
        sources =  service.get_all_sources()
        return JsonResponse({"sources": sources}, safe=False, json_dumps_params={"ensure_ascii": False, "indent": 2})
