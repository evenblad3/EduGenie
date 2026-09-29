import os
import json
import re
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACK_MODELS = ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]



def get_gemini_api_key() -> str:
    for key in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_KEY"]:
        val = os.getenv(key)
        if val:
            return val.strip().strip("'\"")
    return ""


def get_gemini_model(model_name: str = None):
    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name or PRIMARY_MODEL)


async def generate_response(prompt: str, max_tokens: int = 2048) -> str:
    models_to_try = [PRIMARY_MODEL] + [m for m in FALLBACK_MODELS if m != PRIMARY_MODEL]
    last_error = None

    for model_name in models_to_try:
        try:
            model = get_gemini_model(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                ),
            )
            if response and response.text:
                return response.text
        except ValueError:
            raise
        except Exception as e:
            last_error = e
            logger.warning(f"Model {model_name} failed: {e}. Trying fallback...")

    logger.error(f"All Gemini models failed. Last error: {last_error}")
    raise RuntimeError(f"AI service unavailable: {last_error}")


def parse_json_response(text: str):
    cleaned = text.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    array_match = re.search(r"\[\s*\{[\s\S]*\}\s*\]", cleaned)
    if array_match:
        try:
            return json.loads(array_match.group(0))
        except json.JSONDecodeError:
            pass

    obj_match = re.search(r"\{[\s\S]*\}", cleaned)
    if obj_match:
        try:
            return json.loads(obj_match.group(0))
        except json.JSONDecodeError:
            pass

    logger.error(f"Failed to parse JSON from AI response:\n{cleaned[:500]}")
    raise ValueError("Failed to parse AI response as structured data")