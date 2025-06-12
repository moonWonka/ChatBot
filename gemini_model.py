from dotenv import load_dotenv
from config.settings import GEMINI_API_KEY
from prompts.prompts import PROMPT_TENDENCIAS_SENTIMIENTO
import os
from google import genai
from google.genai import types

load_dotenv()

def load_prompt() -> str:
    return PROMPT_TENDENCIAS_SENTIMIENTO

def generate_prompt(user_input: str) -> str:
    """
    Genera el prompt para enviar al modelo Gemini basado en la entrada del usuario.
    """
    return f"{load_prompt()}\n{user_input}"

def call_gemini(user_input: str) -> str:
    """
    Realiza la llamada al modelo Gemini utilizando la biblioteca google-genai.
    """
    print("Llamando al modelo: Gemini")

    client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

    model = "gemini-2.0-flash-lite"
    # Usar generate_prompt para incluir el system prompt
    prompt_text = generate_prompt(user_input)
    contents = [
        types.Content(
            role="user", # El rol sigue siendo "user" pero el texto contiene el system prompt + user input
            parts=[
                types.Part.from_text(text=prompt_text),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text

    return response_text
