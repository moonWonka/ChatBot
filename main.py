from gemini_model import call_gemini, generar_consulta_sql
from db.history_operations import save_conversation, get_all_conversations, get_conversation_by_session_id, generate_session_id

# Variable global para controlar el estado de la conversación
is_conversation_active = False
current_session_id = None

def display_menu():
    print("\n--- Menú Principal ---")
    print("1. Iniciar nuevo chat")
    print("2. Ver historial de conversaciones")
    print("3. Salir")

def start_new_chat():
    global is_conversation_active
    global current_session_id
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
    current_session_id = generate_session_id()
    # print(f"Nueva sesión de conversación iniciada: {current_session_id}") # Optional: for debugging/info

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
            save_conversation(pregunta, respuesta, current_session_id)
        except Exception as e:
            print(f"❌ Error al generar respuesta: {e}")

def view_history():
    print("\n--- Historial de Conversaciones ---")
    conversations = get_all_conversations()
    if not conversations:
        print("No hay conversaciones en el historial.")
        return

    for conv_session in conversations: # conversations now holds session summaries
        first_prompt_short = (conv_session['first_user_prompt'][:75] + '...') if len(conv_session['first_user_prompt']) > 75 else conv_session['first_user_prompt']
        print(f"Sesión ID: {conv_session['session_id']} [{conv_session['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] Inicio: {first_prompt_short}")

    while True:
        try:
            session_id_choice = input("Ingresa el ID de la sesión para ver detalles (o '0' para volver al menú): ").strip() # Renamed choice for clarity
            if session_id_choice == '0':
                break

            # Validate if the chosen session_id exists in the list of displayed sessions
            # conversations is the list from get_all_conversations()
            is_valid_session_id = any(cs['session_id'] == session_id_choice for cs in conversations)

            if is_valid_session_id:
                print("\n--- Detalle de la Conversación (Sesión ID: " + session_id_choice + ") ---")
                detailed_turns = get_conversation_by_session_id(session_id_choice)
                if not detailed_turns:
                    # This case should ideally be rare if is_valid_session_id check is done from the current list
                    print(f"No se encontraron turnos para la sesión ID: {session_id_choice}")
                for turn in detailed_turns:
                    print(f"  ID Turno: {turn['id']} [{turn['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}]") # Added turn ID for context
                    print(f"  Tú: {turn['user_prompt']}")
                    print(f"  Gemini: {turn['ai_response']}")
                    print("  ------------------------------------")
                print("\n")
            else:
                print("ID de sesión no válido o no encontrado en la lista actual. Intenta de nuevo.")
        except Exception as e:
            print(f"Ocurrió un error al procesar la selección: {e}")

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
