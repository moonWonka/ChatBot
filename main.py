from openai_sql_generator import generate_sql_query

def main():
    print("Chatbot SQL con OpenAI (Escribe 'salir' para terminar)\n")
    
    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("¡Hasta luego!")
            break

        if not pregunta.strip():
            print("⚠️ Pregunta vacía. Intenta de nuevo.")
            continue

        try:
            sql = generate_sql_query(pregunta)
            print(f"\n🔍 Consulta generada:\n{sql}\n")
        except Exception as e:
            print(f"❌ Error al generar consulta: {e}")

if __name__ == "__main__":
    main()
