from django.http import JsonResponse
from datetime import datetime, timedelta
from news.services.services import fetch_news, get_all_sources


def convert_objectid(data):
    if isinstance(data, list):
        for doc in data:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
    elif isinstance(data, dict):
        if "_id" in data:
            data["_id"] = str(data["_id"])
    return data


def get_news(request):
    query = request.GET.get("q", "Finance")

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    start = request.GET.get("start", str(yesterday))
    end = request.GET.get("end", str(today))
    max_articles = int(request.GET.get("max_articles", 100))

    source = request.GET.get("source")
    

    # Convertir a datetime
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    data = fetch_news(
        query,
        source,
        start_date,
        end_date,
        max_articles
    )

    # 🔑 Convertimos ObjectId a string antes de devolverlo
    data = convert_objectid(data)

    return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False, "indent": 2})

def get_sources(request):
   
    sources = get_all_sources()

    return JsonResponse(
        {"sources": sources},
        safe=False,
        json_dumps_params={"ensure_ascii": False, "indent": 2}
    )