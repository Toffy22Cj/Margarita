# src/translation_utils.py
from langdetect import detect
from sentence_transformers import SentenceTransformer, util
from src.router import Router
import time

router = Router()  # carga cores desde configs/cores.yaml

# Modelo multilingual para similitud (rápido y bueno)
_EMB_MODEL = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def prompt_for_translation(text: str, source="es", target="en"):
    # Prompt estricto: solo la traducción, sin nada más
    return (
        f"Actúa como un traductor preciso. Traduce del {source} al {target} **exactamente**, "
        "sin añadir, quitar ni comentar. Conserva nombres técnicos (ej. 'Python') sin traducir.\n\n"
        f"Texto: {text}\n\nSalida: SOLO la traducción."
    )

def translate_via_llm(text: str, model_key="translator_llm", source="es", target="en") -> str:
    prompt = prompt_for_translation(text, source=source, target=target)
    # Usa el router para llamar al core configurado (translator_llm)
    return router.send(model_key, prompt).strip()

def back_translate_via_llm(text_en: str, model_key="translator_llm") -> str:
    # traducir de EN -> ES
    prompt = (
        "Actúa como traductor. Traduce del inglés al español exactamente. "
        "Salida: SOLO la traducción.\n\nTexto: " + text_en
    )
    return router.send(model_key, prompt).strip()

def validate_translation_semantic(source_es: str, translated_en: str, threshold=0.75):
    """
    1) Detecta que 'translated_en' esté en inglés.
    2) Back-translate a español y calcula similitud semántica entre source_es y back_translation.
    Devuelve (accept:bool, info:dict)
    """
    info = {}
    # 1) detect language of translated_en
    try:
        lang = detect(translated_en)
    except Exception as e:
        return False, {"reason": "lang_detect_failed", "error": str(e)}

    info["detected_lang"] = lang
    if lang != "en":
        return False, {"reason": "not_english", "detected": lang}

    # 2) back-translation
    back = back_translate_via_llm(translated_en)
    info["back_translation"] = back

    # 3) semantic similarity
    emb_src = _EMB_MODEL.encode(source_es, convert_to_tensor=True)
    emb_back = _EMB_MODEL.encode(back, convert_to_tensor=True)
    score = util.cos_sim(emb_src, emb_back).item()
    info["semantic_score"] = float(score)

    accept = score >= threshold
    info["accepted"] = accept
    return accept, info

# ejemplo de uso:
if __name__ == "__main__":
    s = "Me gusta programar en Python"
    t = translate_via_llm(s)
    ok, details = validate_translation_semantic(s, t)
    print("SOURCE:", s)
    print("TRANSLATION:", t)
    print("OK?", ok)
    print("DETAILS:", details)
