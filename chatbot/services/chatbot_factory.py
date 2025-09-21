from chatbot.services.chat_model_provider import ModelProvider
from chatbot.services.chatbot_service import ChatbotService
from chatbot.services.failover_manager import FailoverManager
from chatbot.services.faqs_manager import FaqsManager
from chatbot.services.text_normalizer import TextNormalizer


class ChatbotFactory:
    """Factory para crear instancias de ChatbotService."""

    @staticmethod
    def create():
        # Dependencias auxiliares
        faqs_manager = FaqsManager()
        normalizer = TextNormalizer()
        failover = FailoverManager()

        # Proveedor de modelo/tokenizer
        provider = ModelProvider()

        # Crear instancia del servicio con dependencias inyectadas
        return ChatbotService(
            faqs_manager=faqs_manager,
            normalizer=normalizer,
            failover=failover,
            model_provider=provider,
        )
