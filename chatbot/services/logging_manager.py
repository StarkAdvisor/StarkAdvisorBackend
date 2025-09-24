


from chatbot.models import ChatLog


class LoggingManager:
    """Gestiona el guardado de logs de interacciones en la base de datos."""

    @staticmethod
    def log_interaction(question: str, answer: str, confidence: float) -> None:
        """
        Guarda un log en la base de datos.
        """
        ChatLog.objects.create(
            question=question,
            answer=answer,
            confidence=confidence
        )
