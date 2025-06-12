from gemini_model import call_gemini, generar_consulta_sql, generate_response_from_data # Added generate_response_from_data
from db.history_operations import save_conversation, get_all_conversations, get_conversation_by_session_id, generate_session_id
from db.connection import execute_query # Added
from prompts.prompts import PROMPT_GENERAR_SQL, PROMPT_ANALISIS_MUSICAL # Added PROMPT_ANALISIS_MUSICAL

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

    print("\n--- Nuevo Chat (Escribe 'salir' para terminar) ---\n")
    modelo_sql_generation = "" # Renamed for clarity
    while modelo_sql_generation.lower() not in ["gemini", "anthropic"]:
        modelo_sql_generation = input("Selecciona el modelo para generación SQL ('gemini' o 'anthropic'): ").strip()
        if modelo_sql_generation.lower() not in ["gemini", "anthropic"]:
            print("⚠️ Modelo no válido. Intenta de nuevo.")

    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("Volviendo al menú principal...")
            is_conversation_active = False
            break

        if not pregunta.strip():
            print("⚠️ Pregunta vacía. Intenta de nuevo.")
            continue

        try:
            estructura_tabla = "" # Remains empty for now

            print(f"Generando consulta SQL con {modelo_sql_generation.capitalize()}...")
            sql_query = generar_consulta_sql(modelo_sql_generation, pregunta, estructura_tabla, PROMPT_GENERAR_SQL)

            # Check if SQL generation was successful and looks like a SELECT query
            if not sql_query or "error" in sql_query.lower() or "sorry" in sql_query.lower() or not sql_query.strip().upper().startswith("SELECT"):
                response_message = f"No se pudo generar una consulta SQL válida o la consulta indica un problema: {sql_query if sql_query else 'Consulta vacía.'}"
                print(f"\n⚠️ {response_message}\n")
                save_conversation(pregunta, f"Error generating SQL: {sql_query if sql_query else 'Consulta vacía.'}", current_session_id)
                continue

            print(f"Ejecutando consulta SQL...")
            db_results = execute_query(sql_query)

            print(f"Generando respuesta final desde los datos...")
            natural_language_response = generate_response_from_data(pregunta, db_results, PROMPT_ANALISIS_MUSICAL)

            print(f"\n💬 Respuesta:\n{natural_language_response}\n")
            save_conversation(pregunta, natural_language_response, current_session_id)

        except Exception as e:
            error_message = f"Error en el flujo del chat: {str(e)}" # str(e) for better error logging
            print(f"❌ {error_message}")
            save_conversation(pregunta, error_message, current_session_id)

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
