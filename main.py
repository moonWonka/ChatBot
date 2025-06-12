from gemini_model import call_gemini
from db.history_operations import save_conversation, get_all_conversations, get_conversation_by_id # Added new imports

is_conversation_active = False

def display_menu():
    print("\n--- Menú Principal ---")
    print("1. Iniciar nuevo chat")
    print("2. Ver historial de conversaciones")
    print("4. Finalizar conversación actual") # New option
    print("5. Salir") # Adjusted option

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
                is_conversation_active = False # End current conversation
                break # Proceed to start a new one
            elif choice == '2':
                print("Volviendo al menú principal...")
                return # Keep is_conversation_active = True
            else:
                print("Opción no válida. Intenta de nuevo.")

    # If we are here, either there was no active conversation,
    # or the user chose to start a new one.
    is_conversation_active = True
    print("\n--- Nuevo Chat con Gemini (Escribe 'salir' para terminar) ---\n")
    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("Volviendo al menú principal...")
            is_conversation_active = False # Reset when chat ends
            break

        if not pregunta.strip():
            print("⚠️ Pregunta vacía. Intenta de nuevo.")
            continue

        try:
            respuesta = call_gemini(pregunta)
            print(f"\n🔍 Respuesta generada por Gemini:\n{respuesta}\n")
            save_conversation(pregunta, respuesta) # Existing save call
        except Exception as e:
            print(f"❌ Error al generar respuesta: {e}")

def view_history():
    print("\n--- Historial de Conversaciones ---")
    conversations = get_all_conversations()
    if not conversations:
        print("No hay conversaciones en el historial.")
        return

    for conv in conversations:
        # Truncate long prompts/responses for brevity in the list
        user_prompt_short = (conv['user_prompt'][:75] + '...') if len(conv['user_prompt']) > 75 else conv['user_prompt']
        print(f"{conv['id']}. [{conv['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] Tú: {user_prompt_short}")

    while True:
        try:
            choice = input("Ingresa el ID de la conversación para ver detalles (o '0' para volver al menú): ")
            if choice == '0':
                break
            conv_id = int(choice)
            # Find by ID from the already fetched list.
            # If performance becomes an issue for very long histories,
            # you might call get_conversation_by_id(conv_id) directly.
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


def main():
    # Comment out or remove cargar_datos() if it's not needed every time
    # cargar_datos()

    while True:
        display_menu()
        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            start_new_chat()
        elif opcion == '2':
            view_history()
        elif opcion == '4': # New option handler
            finalize_conversation()
        elif opcion == '5': # Adjusted option handler
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

# Function to finalize conversation
def finalize_conversation():
    global is_conversation_active
    if is_conversation_active:
        is_conversation_active = False
        print("Conversación actual finalizada.")
    else:
        print("No hay ninguna conversación activa para finalizar.")

if __name__ == "__main__":
    main()
