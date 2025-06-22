from dotenv import load_dotenv
from config.settings import GEMINI_API_KEY, ANTHROPIC_API_KEY
from prompts.prompts import PROMPT_GENERAR_SQL, PROMPT_ANALIZAR_RESPUESTA
from google import genai
from google.genai import types
import anthropic

load_dotenv()

def load_prompt() -> str:
    return PROMPT_GENERAR_SQL

def generate_prompt(user_input: str) -> str:
    """
    Genera el prompt para enviar al modelo Gemini basado en la entrada del usuario.
    """
    return f"{load_prompt()}\n{user_input}"

def call_gemini(prompt: str) -> str:
    """
    Realiza la llamada al modelo Gemini utilizando la biblioteca google-genai.

    Args:
        prompt (str): Prompt completo que incluye la estructura de la tabla y la pregunta.

    Returns:
        str: Respuesta generada por el modelo Gemini.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(response_mime_type="text/plain")

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model="gemini-2.0-flash-lite",
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text

    return response_text.strip()

def call_anthropic(prompt: str) -> str:
    """
    Realiza la llamada al modelo Anthropic utilizando la biblioteca anthropic.

    Args:
        prompt (str): Prompt completo que incluye la estructura de la tabla y la pregunta.

    Returns:
        str: Respuesta generada por el modelo Anthropic.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return message.content[0].text.strip()

def execute_model(modelo: str, prompt: str) -> str:
    """
    Ejecuta el modelo especificado con el prompt proporcionado.

    Args:
        modelo (str): Nombre del modelo a utilizar (Gemini o Anthropic).
        prompt (str): Prompt completo que incluye la estructura de la tabla y la pregunta.

    Returns:
        str: Respuesta generada por el modelo especificado.
    """
    if modelo.lower() == "gemini":
        return call_gemini(prompt)
    elif modelo.lower() == "anthropic":
        return call_anthropic(prompt)
    else:
        raise ValueError("Modelo no soportado: Debe ser 'gemini' o 'anthropic'")

def analizar_respuesta_modelo(respuesta_modelo: str, pregunta: str) -> str:
    """
    Analiza la respuesta generada por el modelo y la ajusta para cumplir con las reglas especificadas.

    Args:
        respuesta_modelo (str): Respuesta generada por el modelo.
        pregunta (str): Pregunta original del usuario.

    Returns:
        str: Respuesta ajustada en lenguaje natural.
    """
    prompt_analisis = PROMPT_ANALIZAR_RESPUESTA.format(
        pregunta=pregunta,
        respuesta_modelo=respuesta_modelo
    )
    
    # Se podría usar cualquiera de los modelos disponibles para el análisis
    # Por defecto usaremos Gemini para el análisis
    return call_gemini(prompt_analisis)
