from dotenv import load_dotenv
from config.settings import GEMINI_API_KEY
from prompts.prompts import PROMPT_GENERAR_SQL
from google import genai
from google.genai import types
import anthropic
import os
import json # Add this import

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
        model="gemini-2.0-flash",
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
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
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
    prompt = f"""Dada la siguiente pregunta:
    "{pregunta}"
    Y la siguiente respuesta generada por el modelo:
    {respuesta_modelo}
    Ajusta la respuesta para cumplir con las siguientes reglas:
    1. Responde directamente sin hacer mención a SQL u otros términos técnicos.
    2. Usa un lenguaje claro, profesional, como si estuvieses conversando con el usuario que efectúa la pregunta.
    3. Presenta la información de manera organizada y fácil de entender. Trata de estructurar los datos y ordenarlos al momento de responder.
    4. Si los datos son limitados o incompletos, proporciona una respuesta con la información disponible y no pidas disculpas.
    5. Utiliza términos propios del ámbito universitario cuando sea posible.
    6. Si los datos incluyen cifras monetarias, utiliza el símbolo $ e incorpora separadores de miles. Los datos monetarios son siempre en pesos chilenos.
    7. No agregues información que no esté explícitamente en los datos obtenidos.
    8. Si la respuesta no puede ser respondida, indica amablemente que no hay datos disponibles e invita a una nueva pregunta.
    9. No agregues a menos que se solicite un análisis de resultados. Sólo entrégalos de manera entendible sin emitir opinión a menos que se solicite.
    10. No hagas supuestos ni hagas sugerencias con los datos. Esto es muy importante.
    11. Envía el resultado de manera precisa y estructurada sin un análisis salvo que se solicite.
    12. Los resultados son utilizados en una conversión tipo chat, por tanto no saludes ni te despidas. Limita a entregar los resultados de manera clara.
    13. IMPORTANTE: Nunca menciones datos técnicos ni pidas disculpas.
    
    ejemplpo exutructura aseguir:
    
    """
    # Aquí podrías integrar un modelo adicional o lógica para ajustar la respuesta según las reglas.


     
    return prompt
