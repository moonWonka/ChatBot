from gemini_model import call_gemini, generar_consulta_sql
from db.history_operations import save_conversation, get_all_conversations, get_conversation_by_id

# Variable global para controlar el estado de la conversación
is_conversation_active = False

def display_menu():
    print("\n--- Menú Principal ---")
    print("1. Iniciar nuevo chat")
    print("2. Ver historial de conversaciones")
    print("3. Salir")

def start_new_chat():
    global is_conversation_active
    if is_conversation_active:
        print("Ya hay una conversación en curso.")
        while True:
            print("Selecciona una opción:")
            print("1. Iniciar una nueva conversación (finalizará la actual)")
            print("2. Volver al menú principal")
            choice = input("Opción: ")
            if choice == '1':
                is_conversation_active = False # Finalizar conversación actual
                break # Proceder a iniciar una nueva
            elif choice == '2':
                print("Volviendo al menú principal...")
                return # Mantener is_conversation_active = True
            else:
                print("Opción no válida. Intenta de nuevo.")

    # Si llegamos aquí, no había conversación activa o el usuario eligió iniciar una nueva.
    is_conversation_active = True

    print("\n--- Nuevo Chat con Gemini o Anthropic (Escribe 'salir' para terminar) ---\n")
    modelo = ""
    while modelo.lower() not in ["gemini", "anthropic"]:
        modelo = input("Selecciona el modelo ('gemini' o 'anthropic'): ").strip()
        if modelo.lower() not in ["gemini", "anthropic"]:
            print("⚠️ Modelo no válido. Intenta de nuevo.")

    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("Volviendo al menú principal...")
            is_conversation_active = False # Finalizar conversación
            break

        if not pregunta.strip():
            print("⚠️ Pregunta vacía. Intenta de nuevo.")
            continue

        try:
            from prompts.prompts import PROMPT_GENERAR_SQL
            estructura_tabla = ""  # Aquí deberías cargar la estructura de la tabla desde la base de datos
            respuesta = generar_consulta_sql(modelo, pregunta, estructura_tabla, PROMPT_GENERAR_SQL)
            print(f"\n🔍 Respuesta generada por {modelo.capitalize()}:\n{respuesta}\n")
            save_conversation(pregunta, respuesta) 
        except Exception as e:
            print(f"❌ Error al generar respuesta: {e}")

def view_history():
    print("\n--- Historial de Conversaciones ---")
    conversations = get_all_conversations()
    if not conversations:
        print("No hay conversaciones en el historial.")
        return

    for conv in conversations:
        user_prompt_short = (conv['user_prompt'][:75] + '...') if len(conv['user_prompt']) > 75 else conv['user_prompt']
        print(f"{conv['id']}. [{conv['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] Tú: {user_prompt_short}")

    while True:
        try:
            choice = input("Ingresa el ID de la conversación para ver detalles (o '0' para volver al menú): ")
            if choice == '0':
                break
            conv_id = int(choice)
            selected_conv = next((c for c in conversations if c['id'] == conv_id), None)

            if selected_conv:
                print("\n--- Detalle de la Conversación ---")
                print(f"ID: {selected_conv['id']}")
                print(f"Fecha: {selected_conv['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Tú: {selected_conv['user_prompt']}")
                print(f"Gemini: {selected_conv['ai_response']}")
                print("------------------------------------\n")
            else:
                print("ID de conversación no válido. Intenta de nuevo.")
        except ValueError:
            print("Entrada no válida. Por favor ingresa un número.")
        except Exception as e:
            print(f"Ocurrió un error: {e}")

def cargar_datos():
    from db.load_data import cargar_datos as cargar_datos_db
    try:
        cargar_datos_db()
        print("✅ Datos cargados exitosamente.")
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")

def main():
    # cargar_datos()
    while True:
        display_menu()
        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            start_new_chat()
        elif opcion == '2':
            view_history()
        elif opcion == '3':
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()
