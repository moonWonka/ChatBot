from gemini_model import call_gemini
from db.history_operations import save_conversation, get_all_conversations, get_conversation_by_id

def display_menu():
    print("\n--- Menú Principal ---")
    print("1. Iniciar nuevo chat")
    print("2. Ver historial de conversaciones")
    print("3. Salir")

def start_new_chat():
    print("\n--- Nuevo Chat con Gemini (Escribe 'salir' para terminar) ---\n")
    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("Volviendo al menú principal...")
            break

        if not pregunta.strip():
            print("⚠️ Pregunta vacía. Intenta de nuevo.")
            continue

        try:
            respuesta = call_gemini(pregunta)
            print(f"\n🔍 Respuesta generada por Gemini:\n{respuesta}\n")
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

def main():
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
