import os
import environ
from django.conf import settings


class FailoverManager:
    """Gestiona la lógica de fallover para respuestas del modelo."""

    def __init__(self):
        # Cargar variables de entorno con fallback por defectoMuy bien
        self._threshold = float(getattr(settings, "FALLOVER_THRESHOLD", 0.1))
        self._message = getattr(settings, "FALLOVER_MESSAGE", 
                                "Lo siento, no puedo responder esa pregunta.")

    def check(self, confidence: float, predicted_answer: str) -> str:
        """
        Retorna la respuesta del modelo si supera el umbral,
        de lo contrario retorna el mensaje de fallover.
        """
        if confidence < self._threshold:
            return self._message
        return predicted_answer
    
    def get_message(self):
        return self._message
