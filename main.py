from openai_sql_generator import generate_sql_query
from db.load_data import main as load_data

def cargar_datos():
    """Carga los datos desde el CSV a la base de datos."""
    print("Cargando datos desde el CSV a la base de datos...")
    load_data()
    print("✅ Datos cargados correctamente.")

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

# Comentar esta línea después de la primera ejecución
# cargar_datos()

if __name__ == "__main__":
    # Cargar datos desde el CSV a la base de datos
    cargar_datos()

    # Iniciar la aplicación del chatbot
    # main()
