from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from .services import get_news_with_sentiment

from datetime import datetime, timedelta
from django.http import JsonResponse



def get_news(request):
    query = request.GET.get("q", "Finance")

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    start = request.GET.get("start", str(yesterday))
    end = request.GET.get("end", str(today))
    max_articles = int(request.GET.get("max_articles", 10))


    domains_param = request.GET.get("domains")
    if domains_param:
        financial_business_news_domains = domains_param.split(",")
    else:
        financial_business_news_domains = None  # se usarán los default del service

    # Convertir a datetime
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    data = get_news_with_sentiment(
        query, start_date, end_date,
        financial_business_news_domains=financial_business_news_domains,
        max_articles=max_articles
    )

    return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False, "indent": 2})
