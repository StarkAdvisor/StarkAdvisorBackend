
import torch
from transformers import pipeline
from langdetect import detect

from chatbot.services.logging_manager import LoggingManager




class ChatbotService:
    

    def __init__(self, faqs_manager, normalizer, failover, model_provider):
        # Gestores auxiliares
        self._faqs_manager = faqs_manager
        self._normalizer = normalizer
        self._failover = failover

        # Modelo y tokenizer desde el ModelProvider
        self._model = model_provider.get_model()
        self._tokenizer = model_provider.get_tokenizer()

        # Crear pipeline
        self._clf = pipeline(
            "text-classification",
            model=self._model,
            tokenizer=self._tokenizer,
            device=0 if torch.cuda.is_available() else -1,
        )


    def get_answer(self, user_question: str) -> str:
        """
        Retorna la respuesta a la pregunta del usuario,
        aplicando normalización, modelo y failover.
        """
        # 1. Detectar idioma automáticamente (es/en)
        try:
            lang = detect(user_question)
            if lang not in ["es", "en"]:
                lang = "es"  # fallback por defecto
        except:
            lang = "es"

        # 2. Normalizar
        clean_q = self._normalizer.normalize(user_question, lang=lang)

        # 3. Predicción del modelo
        
        pred = self._clf(clean_q, truncation=True, max_length=64)[0]
        
        
        label_idx = int(pred["label"].replace("LABEL_", ""))
        confidence = pred["score"]
        

        
        
        # 4. Recuperar FAQ asociada
        faq = self._faqs_manager.get_faq_by_label(label_idx)
        
        if faq:
            predicted_answer = faq.get("answer", {}).get(lang)
            if not predicted_answer:  # si no hay en ese idioma, fallback a español
                predicted_answer = faq.get("answer", {}).get("es", self._failover.get_message())
        else:
            predicted_answer = self._failover.get_message()

        # 5. Logging
        LoggingManager.log_interaction(user_question, predicted_answer, confidence)

        # 6. Failover por baja confianza
        return self._failover.check(confidence, predicted_answer)