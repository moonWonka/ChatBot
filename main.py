from gemini_model import call_gemini

def main():
    print("Chatbot con Gemini (Escribe 'salir' para terminar)\n")

    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("¡Hasta luego!")
            break

        if not pregunta.strip():
            print("⚠️ Pregunta vacía. Intenta de nuevo.")
            continue

        try:
            respuesta = call_gemini(pregunta)
            print(f"\n🔍 Respuesta generada por Gemini:\n{respuesta}\n")
        except Exception as e:
            print(f"❌ Error al generar respuesta: {e}")

# Comentar esta línea después de la primera ejecución
# cargar_datos()

if __name__ == "__main__":
    # Cargar datos desde el CSV a la base de datos
    # cargar_datos()

    # Iniciar la aplicación del chatbot
    main()
