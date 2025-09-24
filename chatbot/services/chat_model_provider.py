from transformers import AutoModelForSequenceClassification, AutoTokenizer
from django.conf import settings

from transformers import AutoModelForSequenceClassification, AutoTokenizer
from django.conf import settings

class ModelProvider:
    """Singleton encargado de proveer modelo y tokenizer de HuggingFace."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ModelProvider, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        model_path = getattr(settings, "FAQ_MODEL_PATH", "./faq_model_2")
        self._model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self._tokenizer = AutoTokenizer.from_pretrained(model_path)

        self._initialized = True

    # --- Getters explícitos ---
    def get_model(self):
        return self._model

    def get_tokenizer(self):
        return self._tokenizer
