import json
from typing import Dict, List, Any
from django.conf import settings


class FaqsManager:
    _instance = None  

    def __new__(cls, *args, **kwargs):
        """Controla la creación de instancia única (Singleton)."""
        if cls._instance is None:
            cls._instance = super(FaqsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
  
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._faq_path = settings.FAQ_PATH
        self._normalized_path = settings.FAQ_NORMALIZED_PATH
        self._faqs_original = self._load_json(self._faq_path)
        self._faqs_normalized = self._load_json(self._normalized_path)

        # Mapas para relacionar labels internos con IDs reales
        # Mapas para relacionar labels internos con IDs reales
        
        self._label_to_id = {idx: faq["id"] for idx, faq in enumerate(self._faqs_normalized)}
        self._id_to_label = {faq["id"]: idx for idx, faq in enumerate(self._faqs_normalized)}




        self._initialized = True  # bandera para no recargar en llamadas futuras

    def _load_json(self, path: str) -> List[Dict[str, Any]]:
    
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)["faqs"]


    def get_original_faqs(self) -> List[Dict[str, Any]]:
        return self._faqs_original

    def get_normalized_faqs(self) -> List[Dict[str, Any]]:
        return self._faqs_normalized

    def get_label_by_id(self, faq_id: int) -> int:
        return self._id_to_label.get(faq_id)

    def get_id_by_label(self, label: int) -> int:
        return self._label_to_id.get(label)


    def get_faq_by_id(self, faq_id: int) -> Dict[str, Any]:
        return next((faq for faq in self._faqs_original if faq["id"] == faq_id), None)

    def get_faq_by_label(self, label: int) -> Dict[str, Any]:
        
        faq_id = self.get_id_by_label(label)
        
        return self.get_faq_by_id(faq_id) if faq_id else None
