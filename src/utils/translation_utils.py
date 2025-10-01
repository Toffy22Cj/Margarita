# [file name]: src/utils/translation_utils.py
from langdetect import detect
from sentence_transformers import SentenceTransformer, util
import time

class TranslationUtils:
    """
    Utilidades para traducción y validación semántica
    """
    
    def __init__(self):
        self._router = None
        self._emb_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    
    def _get_router(self):
        if self._router is None:
            from src.routes.router import Router
            self._router = Router()
        return self._router
    
    def prompt_for_translation(self, text: str, source="es", target="en"):
        return (
            f"Actúa como un traductor preciso. Traduce del {source} al {target} **exactamente**, "
            "sin añadir, quitar ni comentar. Conserva nombres técnicos (ej. 'Python') sin traducir.\n\n"
            f"Texto: {text}\n\nSalida: SOLO la traducción."
        )
    
    def translate_via_llm(self, text: str, model_key="translator_llm", source="es", target="en") -> str:
        router = self._get_router()
        prompt = self.prompt_for_translation(text, source=source, target=target)
        return router.send(model_key, prompt).strip()
    
    def back_translate_via_llm(self, text_en: str, model_key="translator_llm") -> str:
        router = self._get_router()
        prompt = (
            "Actúa como traductor. Traduce del inglés al español exactamente. "
            "Salida: SOLO la traducción.\n\nTexto: " + text_en
        )
        return router.send(model_key, prompt).strip()
    
    def validate_translation_semantic(self, source_es: str, translated_en: str, threshold=0.75):
        info = {}
        try:
            lang = detect(translated_en)
        except Exception as e:
            return False, {"reason": "lang_detect_failed", "error": str(e)}

        info["detected_lang"] = lang
        if lang != "en":
            return False, {"reason": "not_english", "detected": lang}

        back = self.back_translate_via_llm(translated_en)
        info["back_translation"] = back

        emb_src = self._emb_model.encode(source_es, convert_to_tensor=True)
        emb_back = self._emb_model.encode(back, convert_to_tensor=True)
        score = util.cos_sim(emb_src, emb_back).item()
        info["semantic_score"] = float(score)

        accept = score >= threshold
        info["accepted"] = accept
        return accept, info


# Funciones de conveniencia (para mantener compatibilidad)
_translation_utils = TranslationUtils()

def translate_via_llm(text: str, model_key="translator_llm", source="es", target="en") -> str:
    return _translation_utils.translate_via_llm(text, model_key, source, target)

def validate_translation_semantic(source_es: str, translated_en: str, threshold=0.75):
    return _translation_utils.validate_translation_semantic(source_es, translated_en, threshold)


if __name__ == "__main__":
    s = "Me gusta programar en Python"
    t = translate_via_llm(s)
    ok, details = validate_translation_semantic(s, t)
    print("SOURCE:", s)
    print("TRANSLATION:", t)
    print("OK?", ok)
    print("DETAILS:", details)