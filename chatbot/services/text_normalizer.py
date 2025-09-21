
import unicodedata

import spacy


class TextNormalizer:

    def __init__(self):
        # Modelos de spaCy privados para procesamiento de lenguaje
        # _nlp_es -> modelo para español
        # _nlp_en -> modelo para inglés
        self._nlp_es = spacy.load("es_core_news_sm")
        self._nlp_en = spacy.load("en_core_web_sm")


    def normalize(self, text: str, lang: str = "es") -> str:
        """
        Normaliza un texto:
        - Elimina signos de interrogación
        - Pone en minúsculas y elimina tildes
        - Aplica lematización según el idioma
        - Elimina espacios dobles
        """
        # Not quest signs
        text = text.replace("¿", "").replace("?", "")

        # Minúsculas y quitar tildes
        text = text.lower()
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )

        # Lemmatización con el modelo correcto
        nlp = self._nlp_es if lang == "es" else self._nlp_en
        doc = nlp(text)
        lemmatized = " ".join([token.lemma_ for token in doc])

        # Eliminar espacios dobles
        lemmatized = " ".join(lemmatized.split())

        return lemmatized