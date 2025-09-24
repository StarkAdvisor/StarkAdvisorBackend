from django.http import JsonResponse, HttpRequest
from django.views import View
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from chatbot.services.chatbot_factory import ChatbotFactory

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name="dispatch")
class ChatbotView(View):
    """API View para interactuar con el Chatbot."""

    def post(self, request: HttpRequest):
      
            # 1. Parsear body (esperamos JSON con { "question": "...", "lang": "es/en" })
            body = json.loads(request.body.decode("utf-8"))
            question = body.get("question")

            if not question:
                return JsonResponse(
                    {"error": "El campo 'question' es obligatorio."},
                    status=400,
                    json_dumps_params={"ensure_ascii": False, "indent": 2},
                )

            # 2. Crear servicio desde el Factory
            service = ChatbotFactory.create()

            # 3. Obtener respuesta
            answer= service.get_answer(question)

            # 4. Retornar en JSON
            return JsonResponse(
                {
                    "question": question,
                    "answer": answer
                },
                safe=False,
                json_dumps_params={"ensure_ascii": False, "indent": 2},
            )

      
