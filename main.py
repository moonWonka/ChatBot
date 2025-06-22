from ia_model import execute_model
from db.history_operations import save_conversation, get_all_conversations, get_conversation_by_session_id, generate_session_id, get_session_summary, delete_session, search_conversations
from db.connection import execute_query # Added
from prompts.prompts import (
    PROMPT_GENERAR_SQL, 
    PROMPT_RESPUESTA_NATURAL, 
    PROMPT_CONTEXTO_CONVERSACIONAL,
    PROMPT_VALIDAR_PREGUNTA
)

# Variable global para controlar el estado de la conversación
is_conversation_active = False
current_session_id = None

def display_menu():
    print("\n" + "="*60)
    print("🤖 ASISTENTE MUSICAL INTELIGENTE")
    print("="*60)
    print("🎵 Tu compañero para explorar el mundo de la música")
    print("\n🚀 Opciones disponibles:")
    print("1. 💬 Iniciar nuevo chat")
    print("2. 📚 Ver historial de conversaciones") 
    print("3. ⚙️  Configuración y utilidades")
    print("4. ❌ Salir")
    print("-"*60)

def start_new_chat():
    global is_conversation_active
    global current_session_id

    print("\n" + "="*60)
    print("💬 NUEVO CHAT")
    print("="*60)

    # Verificar si hay una conversación activa
    if is_conversation_active:
        print("⚠️  Ya hay una conversación en curso.")
        print("\n🔄 Opciones disponibles:")
        print("1. Iniciar una nueva conversación (finalizará la actual)")
        print("2. Volver al menú principal")
        print("-"*40)
        
        while True:
            choice = input("Selecciona una opción (1-2): ").strip()
            if choice == '1':
                print("🔄 Finalizando conversación actual...")
                is_conversation_active = False  # Finalizar conversación actual
                break  # Proceder a iniciar una nueva
            elif choice == '2':
                print("🔙 Volviendo al menú principal...")
                return  # Mantener is_conversation_active = True
            else:
                print("❌ Opción no válida. Por favor selecciona 1 o 2.")

    # Iniciar nueva conversación
    print("🚀 Iniciando nueva conversación...")
    is_conversation_active = True
    current_session_id = generate_session_id()
    session_short = current_session_id[:8]
    print(f"📝 ID de sesión: {session_short}...")

    modelo_seleccionado = seleccionar_modelo()
    print(f"✅ Modelo seleccionado: {modelo_seleccionado.capitalize()}")
    print("\n" + "="*60)
    print("💬 CONVERSACIÓN ACTIVA")
    print("="*60)
    print("💡 Puedes preguntar sobre música, artistas, canciones, géneros, etc.")
    print("🧠 El asistente recordará el contexto de esta conversación")
    print("💡 Puedes usar referencias como 'él', 'esa canción', 'más como esa', etc.")
    print("🔍 Escribe 'contexto' para ver el historial de esta conversación")
    print("💡 Escribe 'salir', 'exit' o 'quit' para volver al menú principal")
    print("-"*60)

    while True:
        pregunta = input("\n👤 Tú: ").strip()
        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("\n🔙 Volviendo al menú principal...")
            is_conversation_active = False
            break

        if not pregunta:
            print("⚠️  Pregunta vacía. Por favor, escribe algo.")
            continue

        # Comando especial para ver el contexto
        if pregunta.lower() in ["contexto", "historial", "ver contexto"]:
            mostrar_contexto_actual()
            continue

        manejar_pregunta(pregunta, modelo_seleccionado)


def seleccionar_modelo() -> str:
    """Permite al usuario seleccionar el modelo para generación SQL."""
    print("\n🧠 SELECCIÓN DE MODELO DE IA")
    print("-"*40)
    print("1. 🔹 Gemini (Google)")
    print("2. 🔸 Anthropic (Claude)")
    print("-"*40)
    
    while True:
        opcion = input("Selecciona el modelo (1-2): ")

        if opcion == '1':
            return "gemini"
        elif opcion == '2':
            return "anthropic"
        else:
            print("❌ Opción no válida. Por favor selecciona 1 o 2.")


def manejar_pregunta(pregunta: str, modelo_seleccionado: str):
    """Genera la consulta SQL, la ejecuta y responde al usuario."""
    try:
        print(f"\n🔄 Procesando...")
        
        # Procesar pregunta con contexto conversacional
        pregunta_contextualizada = procesar_pregunta_con_contexto(pregunta, modelo_seleccionado, current_session_id)
        
        # Validar si la pregunta es válida antes de generar consulta SQL
        validacion_resultado = execute_model(modelo_seleccionado, PROMPT_VALIDAR_PREGUNTA.format(pregunta=pregunta_contextualizada))
        
        if validacion_resultado.startswith("FUERA_CONTEXTO"):
            response_message = "La pregunta está fuera del contexto de música y canciones disponible."
            print(f"\n⚠️  {response_message}\n")
            return
        elif validacion_resultado.startswith("ACLARAR:"):
            response_message = validacion_resultado.replace("ACLARAR:", "").strip()
            print(f"\n⚠️  {response_message}\n")
            return
        elif not validacion_resultado.startswith("VALIDA"):
            response_message = "No se pudo validar la pregunta. Por favor, reformúlala."
            print(f"\n⚠️  {response_message}\n")
            return        print("⚙️  Generando consulta SQL...")
        sql_query = execute_model(modelo_seleccionado, PROMPT_GENERAR_SQL.format(pregunta=pregunta_contextualizada))

        if not sql_query:
            response_message = "No se pudo generar una consulta SQL válida."
            print(f"\n⚠️  {response_message}\n")
            return

        if sql_query.strip().lower().startswith("no"):
            response_message = "La consulta generada indica que no está dentro del contexto disponible."
            print(f"\n⚠️  {response_message}\n")
            return

        if sql_query.strip().lower().startswith("sql"):
            sql_query = sql_query[sql_query.lower().find("sql") + 3:].strip()
            
        # Limpiar backticks y markdown que puedan aparecer
        sql_query = sql_query.replace("```sql", "").replace("```", "").replace("`", "").strip()
        
        print("🔍 Consultando base de datos...")
        db_results = execute_query(sql_query)

        # Generar respuesta en lenguaje natural basada en los resultados
        natural_language_response = execute_model(
            modelo_seleccionado, 
            PROMPT_RESPUESTA_NATURAL.format(pregunta=pregunta_contextualizada, resultados_db=db_results)
        )

        print(f"\n🤖 Respuesta:")
        print("─" * 50)
        print(natural_language_response)
        print("─" * 50)
        
        # IMPORTANTE: Guardar la pregunta ORIGINAL del usuario, no la contextualizada
        save_conversation(pregunta, natural_language_response, current_session_id)

    except Exception as e:
        error_message = f"Error en el procesamiento: {str(e)}"
        print(f"\n❌ {error_message}")
        print("💡 Intenta reformular tu pregunta o contacta al administrador.")
        # No guardamos errores de excepción tampoco

def view_history():
    """Interfaz mejorada para ver y gestionar el historial de conversaciones."""
    while True:
        print("\n" + "="*60)
        print("📚 HISTORIAL DE CONVERSACIONES")
        print("="*60)
        
        # Menú de opciones del historial
        print("\n🔍 Opciones disponibles:")
        print("1. Ver todas las sesiones")
        print("2. Buscar en conversaciones")
        print("3. Ver detalles de una sesión específica")
        print("4. Continuar una conversación existente")
        print("5. Eliminar una sesión")
        print("0. Volver al menú principal")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == '0':
            break
        elif opcion == '1':
            mostrar_todas_las_sesiones()
        elif opcion == '2':
            buscar_conversaciones()
        elif opcion == '3':
            ver_detalles_sesion()
        elif opcion == '4':
            continuar_conversacion_existente()
        elif opcion == '5':
            eliminar_sesion()
        else:
            print("❌ Opción no válida. Intenta de nuevo.")

def mostrar_todas_las_sesiones():
    """Muestra todas las sesiones de conversación con formato mejorado."""
    print("\n" + "-"*80)
    print("📋 TODAS LAS SESIONES")
    print("-"*80)
    
    conversations = get_all_conversations()
    if not conversations:
        print("📭 No hay conversaciones en el historial.")
        input("\nPresiona Enter para continuar...")
        return
    
    print(f"\n📊 Total de sesiones encontradas: {len(conversations)}\n")
    
    for i, conv_session in enumerate(conversations, 1):
        # Crear un ID corto más legible
        session_short = conv_session['session_id'][:8]
        first_prompt_short = (conv_session['first_user_prompt'][:60] + '...') if len(conv_session['first_user_prompt']) > 60 else conv_session['first_user_prompt']
        
        print(f"#{i:2d} │ ID: {session_short}... │ {conv_session['timestamp'].strftime('%d/%m/%Y %H:%M')}")
        print(f"    │ Pregunta: {first_prompt_short}")
        print(f"    └{'─'*70}")
    
    input("\nPresiona Enter para continuar...")

def buscar_conversaciones():
    """Permite buscar en el historial de conversaciones."""
    print("\n" + "-"*50)
    print("🔍 BUSCAR EN CONVERSACIONES")
    print("-"*50)
    
    termino = input("Ingresa el término a buscar: ").strip()
    if not termino:
        print("❌ Término de búsqueda vacío.")
        return
    
    resultados = search_conversations(termino)
    if not resultados:
        print(f"🔍 No se encontraron conversaciones con el término: '{termino}'")
        input("\nPresiona Enter para continuar...")
        return
    
    print(f"\n📊 Se encontraron {len(resultados)} resultado(s) para: '{termino}'\n")
    
    for i, resultado in enumerate(resultados, 1):
        session_short = resultado['session_id'][:8]
        print(f"🔹 Resultado #{i}")
        print(f"   ID Sesión: {session_short}...")
        print(f"   Fecha: {resultado['timestamp'].strftime('%d/%m/%Y %H:%M')}")
        print(f"   Pregunta: {resultado['user_prompt'][:80]}{'...' if len(resultado['user_prompt']) > 80 else ''}")
        print(f"   Respuesta: {resultado['ai_response'][:80]}{'...' if len(resultado['ai_response']) > 80 else ''}")
        print("   " + "-"*60)
    
    input("\nPresiona Enter para continuar...")

def ver_detalles_sesion():
    """Permite ver los detalles completos de una sesión específica."""
    print("\n" + "-"*50)
    print("🔍 VER DETALLES DE SESIÓN")
    print("-"*50)
    
    conversations = get_all_conversations()
    if not conversations:
        print("📭 No hay conversaciones en el historial.")
        input("\nPresiona Enter para continuar...")
        return
    
    # Mostrar lista numerada de sesiones
    print("\n📋 Sesiones disponibles:")
    for i, conv in enumerate(conversations, 1):
        session_short = conv['session_id'][:8]
        first_prompt_short = (conv['first_user_prompt'][:50] + '...') if len(conv['first_user_prompt']) > 50 else conv['first_user_prompt']
        print(f"{i:2d}. {session_short}... │ {conv['timestamp'].strftime('%d/%m/%Y %H:%M')} │ {first_prompt_short}")
    
    try:
        opcion = input(f"\nSelecciona una sesión (1-{len(conversations)}) o '0' para cancelar: ").strip()
        if opcion == '0':
            return
        
        indice = int(opcion) - 1
        if 0 <= indice < len(conversations):
            session_id = conversations[indice]['session_id']
            mostrar_conversacion_completa(session_id)
        else:
            print("❌ Número de sesión no válido.")
            input("\nPresiona Enter para continuar...")
    except ValueError:
        print("❌ Por favor ingresa un número válido.")
        input("\nPresiona Enter para continuar...")

def mostrar_conversacion_completa(session_id: str):
    """Muestra una conversación completa con formato mejorado."""
    print("\n" + "="*80)
    print("💬 CONVERSACIÓN COMPLETA")
    print("="*80)
    
    # Obtener resumen de la sesión
    resumen = get_session_summary(session_id)
    if resumen:
        print(f"📊 Resumen de la sesión:")
        print(f"   • ID: {session_id[:8]}...")
        print(f"   • Total de intercambios: {resumen['total_turns']}")
        print(f"   • Inicio: {resumen['session_start'].strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   • Final: {resumen['session_end'].strftime('%d/%m/%Y %H:%M:%S')}")
        if resumen['duration_minutes'] > 0:
            print(f"   • Duración: {resumen['duration_minutes']:.1f} minutos")
        print("-"*80)
    
    # Obtener y mostrar todos los turnos
    turnos = get_conversation_by_session_id(session_id)
    if not turnos:
        print("❌ No se encontraron detalles para esta sesión.")
        input("\nPresiona Enter para continuar...")
        return
    
    for i, turno in enumerate(turnos, 1):
        print(f"\n🔹 Intercambio #{i} [{turno['timestamp'].strftime('%H:%M:%S')}]")
        print(f"👤 Usuario: {turno['user_prompt']}")
        print(f"🤖 Asistente: {turno['ai_response']}")
        if i < len(turnos):  # No mostrar separador después del último turno
            print("   " + "·"*60)
    
    print("\n" + "="*80)
    input("Presiona Enter para continuar...")

def eliminar_sesion():
    """Permite eliminar una sesión específica del historial."""
    print("\n" + "-"*50)
    print("🗑️  ELIMINAR SESIÓN")
    print("-"*50)
    
    conversations = get_all_conversations()
    if not conversations:
        print("📭 No hay conversaciones en el historial.")
        input("\nPresiona Enter para continuar...")
        return
    
    # Mostrar lista numerada de sesiones
    print("\n📋 Sesiones disponibles para eliminar:")
    for i, conv in enumerate(conversations, 1):
        session_short = conv['session_id'][:8]
        first_prompt_short = (conv['first_user_prompt'][:50] + '...') if len(conv['first_user_prompt']) > 50 else conv['first_user_prompt']
        print(f"{i:2d}. {session_short}... │ {conv['timestamp'].strftime('%d/%m/%Y %H:%M')} │ {first_prompt_short}")
    
    try:
        opcion = input(f"\nSelecciona una sesión para eliminar (1-{len(conversations)}) o '0' para cancelar: ").strip()
        if opcion == '0':
            return
        
        indice = int(opcion) - 1
        if 0 <= indice < len(conversations):
            session_id = conversations[indice]['session_id']
            session_short = session_id[:8]
            
            # Confirmación de eliminación
            confirmacion = input(f"\n⚠️  ¿Estás seguro de que quieres eliminar la sesión {session_short}...? (si/no): ").strip().lower()
            if confirmacion in ['si', 'sí', 's', 'yes', 'y']:
                if delete_session(session_id):
                    print(f"✅ Sesión {session_short}... eliminada exitosamente.")
                else:
                    print(f"❌ Error al eliminar la sesión {session_short}...")
            else:
                print("❌ Eliminación cancelada.")
            
            input("\nPresiona Enter para continuar...")
        else:
            print("❌ Número de sesión no válido.")
            input("\nPresiona Enter para continuar...")
    except ValueError:
        print("❌ Por favor ingresa un número válido.")
        input("\nPresiona Enter para continuar...")

def cargar_datos():
    """Carga los datos de Spotify en la base de datos."""
    print("\n" + "-"*50)
    print("🔄 CARGA DE DATOS DE SPOTIFY")
    print("-"*50)
    
    from db.load_data import cargar_datos_spotify
    try:
        print("� Iniciando proceso de carga...")
        cargar_datos_spotify()
        print("✅ Datos de Spotify cargados exitosamente.")
        print("🎵 La base de datos está lista para consultas.")
    except Exception as e:
        print(f"❌ Error durante la carga de datos: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        import traceback
        print(f"📋 Detalles técnicos: {traceback.format_exc()}")
        print("💡 Contacta al administrador si el problema persiste.")
    
    input("\nPresiona Enter para continuar...")

def menu_configuracion():
    """Menú de configuración y utilidades del sistema."""
    while True:
        print("\n" + "="*60)
        print("⚙️  CONFIGURACIÓN Y UTILIDADES")
        print("="*60)
        
        print("\n🔧 Opciones disponibles:")
        print("1. 🔄 Cargar datos de Spotify")
        print("2. 📊 Estadísticas de la base de datos")
        print("3. 🧹 Limpiar todo el historial")
        print("4. 🔍 Verificar conexión a la base de datos")
        print("0. 🔙 Volver al menú principal")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == '0':
            break
        elif opcion == '1':
            cargar_datos()
        elif opcion == '2':
            mostrar_estadisticas_db()
        elif opcion == '3':
            limpiar_historial_completo()
        elif opcion == '4':
            verificar_conexion_db()
        else:
            print("❌ Opción no válida. Intenta de nuevo.")

def mostrar_estadisticas_db():
    """Muestra estadísticas de la base de datos."""
    print("\n" + "-"*50)
    print("📊 ESTADÍSTICAS DE LA BASE DE DATOS")
    print("-"*50)
    
    try:
        from db.connection import get_connection
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            
            # Estadísticas de conversaciones
            cursor.execute("SELECT COUNT(*) FROM conversation_history")
            total_conversaciones = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT session_id) FROM conversation_history")
            total_sesiones = cursor.fetchone()[0]
            
            # Estadísticas de música
            cursor.execute("SELECT COUNT(*) FROM tracks")
            total_canciones = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM artists")
            total_artistas = cursor.fetchone()[0]
            
            print(f"💬 Conversaciones totales: {total_conversaciones}")
            print(f"📝 Sesiones únicas: {total_sesiones}")
            print(f"🎵 Canciones en DB: {total_canciones}")
            print(f"🎤 Artistas en DB: {total_artistas}")
            
            # Promedio de intercambios por sesión
            if total_sesiones > 0:
                promedio = total_conversaciones / total_sesiones
                print(f"📈 Promedio de intercambios por sesión: {promedio:.1f}")
            
            cursor.close()
            conn.close()
            print("\n✅ Estadísticas obtenidas exitosamente.")
            
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
    
    input("\nPresiona Enter para continuar...")

def limpiar_historial_completo():
    """Permite limpiar completamente el historial de conversaciones."""
    print("\n" + "-"*50)
    print("🧹 LIMPIAR HISTORIAL COMPLETO")
    print("-"*50)
    
    print("⚠️  ADVERTENCIA: Esta acción eliminará TODAS las conversaciones del historial.")
    print("Esta acción NO se puede deshacer.")
    
    confirmacion1 = input("\n¿Estás seguro de que quieres continuar? (si/no): ").strip().lower()
    if confirmacion1 not in ['si', 'sí', 's', 'yes', 'y']:
        print("❌ Operación cancelada.")
        input("\nPresiona Enter para continuar...")
        return
    
    confirmacion2 = input("Por favor confirma escribiendo 'ELIMINAR TODO': ").strip()
    if confirmacion2 != 'ELIMINAR TODO':
        print("❌ Confirmación incorrecta. Operación cancelada.")
        input("\nPresiona Enter para continuar...")
        return
    
    try:
        from db.connection import get_connection
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversation_history")
            filas_eliminadas = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            print(f"✅ Se eliminaron {filas_eliminadas} conversaciones del historial.")
        else:
            print("❌ No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"❌ Error limpiando historial: {e}")
    
    input("\nPresiona Enter para continuar...")

def verificar_conexion_db():
    """Verifica la conexión a la base de datos."""
    print("\n" + "-"*50)
    print("🔍 VERIFICAR CONEXIÓN A BASE DE DATOS")
    print("-"*50)
    
    try:
        from db.connection import get_connection
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if resultado:
                print("✅ Conexión a la base de datos exitosa.")
                print("🔌 La base de datos está respondiendo correctamente.")
            else:
                print("⚠️  Conexión establecida pero no hay respuesta.")
        else:
            print("❌ No se pudo establecer conexión con la base de datos.")
            print("💡 Verifica la configuración de conexión.")
            
    except Exception as e:
        print(f"❌ Error verificando conexión: {e}")
        print("💡 Verifica que el servidor de base de datos esté activo.")
    
    input("\nPresiona Enter para continuar...")

def obtener_historial_conversacion_actual(session_id: str, limite: int = 5) -> str:
    """Obtiene el historial reciente de la conversación actual para contexto."""
    try:
        turnos = get_conversation_by_session_id(session_id)
        if not turnos:
            return "No hay historial previo en esta conversación."
        
        # Tomar solo los últimos turnos para evitar contexto muy largo
        turnos_recientes = turnos[-limite:] if len(turnos) > limite else turnos
        
        historial = []
        for i, turno in enumerate(turnos_recientes, 1):
            historial.append(f"Intercambio {i}:")
            historial.append(f"Usuario: {turno['user_prompt']}")
            historial.append(f"Asistente: {turno['ai_response'][:200]}{'...' if len(turno['ai_response']) > 200 else ''}")
            historial.append("")  # Línea en blanco para separar
        
        return "\n".join(historial)
    except Exception as e:
        print(f"⚠️  Error obteniendo historial: {e}")
        return "No se pudo obtener el historial de la conversación."

def procesar_pregunta_con_contexto(pregunta: str, modelo_seleccionado: str, session_id: str) -> str:
    """Procesa la pregunta del usuario considerando el contexto conversacional."""
    # Obtener historial de la conversación actual
    historial = obtener_historial_conversacion_actual(session_id)
      # Si no hay historial previo, la pregunta se mantiene igual
    if "No hay historial previo" in historial:
        return pregunta
    
    try:
        # Usar el prompt de contexto para mejorar la pregunta
        contexto_resultado = execute_model(
                modelo_seleccionado,            
                PROMPT_CONTEXTO_CONVERSACIONAL.format(
                    historial_conversacion=historial,
                    pregunta_actual=pregunta
            )
        )
        
        if contexto_resultado.startswith("INDEPENDIENTE:"):
            # La pregunta es clara por sí sola
            pregunta_final = contexto_resultado.replace("INDEPENDIENTE:", "").strip()
            return pregunta_final
        elif contexto_resultado.startswith("CONTEXTUALIZADA:"):
            # La pregunta fue mejorada con contexto
            pregunta_final = contexto_resultado.replace("CONTEXTUALIZADA:", "").strip()
            return pregunta_final
        else:
            # Fallback: usar pregunta original
            return pregunta
            
    except Exception as e:
        print(f"⚠️  Error procesando contexto: {e}")
        return pregunta  # Fallback a pregunta original

def mostrar_contexto_actual():
    """Muestra el contexto actual de la conversación."""
    if not current_session_id:
        print("⚠️  No hay una conversación activa.")
        return
    
    print("\n" + "="*50)
    print("🧠 CONTEXTO DE LA CONVERSACIÓN ACTUAL")
    print("="*50)
    
    historial = obtener_historial_conversacion_actual(current_session_id, 3)
    
    if "No hay historial previo" in historial:
        print("📭 Esta es la primera pregunta de la conversación.")
        print("💡 A partir de la próxima pregunta, el asistente recordará el contexto.")
    else:
        print("📋 Últimos intercambios en esta conversación:")
        print("-"*50)
        print(historial)
    
    print("="*50)
    print("💡 Tip: Puedes usar referencias como 'él', 'esa canción', 'más como esa', etc.")
    print("💡 El asistente usará este contexto para entender mejor tus preguntas.")


def main():
    """Función principal del programa."""
    print("🚀 Iniciando Asistente Musical Inteligente...")
    # cargar_datos()  # Descomentado para carga automática si es necesario
    
    while True:
        display_menu()
        opcion = input("\nSelecciona una opción (1-4): ").strip()

        if opcion == '1':
            start_new_chat()
        elif opcion == '2':
            view_history()
        elif opcion == '3':
            menu_configuracion()
        elif opcion == '4':
            print("\n" + "="*50)
            print("👋 ¡Gracias por usar el Asistente Musical!")
            print("🎵 ¡Hasta la próxima!")
            print("="*50)
            break
        else:
            print("❌ Opción no válida. Por favor selecciona una opción del 1 al 4.")

def continuar_conversacion_existente():
    """Permite al usuario continuar una conversación existente desde el historial."""
    global is_conversation_active, current_session_id
    
    print("\n" + "="*60)
    print("🔄 CONTINUAR CONVERSACIÓN EXISTENTE")
    print("="*60)
    
    # Verificar si ya hay una conversación activa
    if is_conversation_active:
        print("⚠️  Ya hay una conversación activa.")
        print(f"📝 ID de sesión actual: {current_session_id[:8]}...")
        print("\n🔄 Opciones disponibles:")
        print("1. Finalizar conversación actual y continuar otra")
        print("2. Cancelar y volver al menú de historial")
        print("-"*40)
        
        while True:
            choice = input("Selecciona una opción (1-2): ").strip()
            if choice == '1':
                print("🔄 Finalizando conversación actual...")
                is_conversation_active = False
                current_session_id = None
                break
            elif choice == '2':
                print("🔙 Regresando al menú de historial...")
                return
            else:
                print("❌ Opción no válida. Por favor selecciona 1 o 2.")
    
    # Mostrar sesiones disponibles
    conversations = get_all_conversations()
    if not conversations:
        print("📭 No hay conversaciones en el historial para continuar.")
        input("\nPresiona Enter para continuar...")
        return
    
    print(f"\n📋 Conversaciones disponibles para continuar ({len(conversations)} sesiones):")
    print("-"*70)
    
    for i, conv in enumerate(conversations, 1):
        session_short = conv['session_id'][:8]
        first_prompt_short = (conv['first_user_prompt'][:45] + '...') if len(conv['first_user_prompt']) > 45 else conv['first_user_prompt']
        
        # Obtener información adicional de la sesión
        resumen = get_session_summary(conv['session_id'])
        total_intercambios = resumen.get('total_turns', 0) if resumen else 0
        
        print(f"{i:2d}. ID: {session_short}... │ {conv['timestamp'].strftime('%d/%m/%Y %H:%M')}")
        print(f"    Inicio: {first_prompt_short}")
        print(f"    Intercambios: {total_intercambios} │ Última actividad: {conv['timestamp'].strftime('%H:%M')}")
        print(f"    └{'─'*60}")
    
    try:
        print(f"\n🔍 Opciones:")
        print("• Ingresa el número de la conversación que quieres continuar")
        print("• Escribe '0' para cancelar")
        
        opcion = input(f"\nSelecciona una conversación (1-{len(conversations)}) o '0' para cancelar: ").strip()
        if opcion == '0':
            print("❌ Operación cancelada.")
            input("\nPresiona Enter para continuar...")
            return
        
        indice = int(opcion) - 1
        if 0 <= indice < len(conversations):
            session_id = conversations[indice]['session_id']
            session_short = session_id[:8]
            
            # Mostrar resumen de la conversación a continuar
            print(f"\n📋 Preparando para continuar conversación {session_short}...")
            mostrar_resumen_conversacion(session_id)
            
            # Confirmar continuación
            confirmacion = input(f"\n¿Quieres continuar esta conversación? (si/no): ").strip().lower()
            if confirmacion in ['si', 'sí', 's', 'yes', 'y']:
                iniciar_continuacion_conversacion(session_id)
            else:
                print("❌ Continuación cancelada.")
                input("\nPresiona Enter para continuar...")
        else:
            print("❌ Número de conversación no válido.")
            input("\nPresiona Enter para continuar...")
    except ValueError:
        print("❌ Por favor ingresa un número válido.")
        input("\nPresiona Enter para continuar...")

def mostrar_resumen_conversacion(session_id: str):
    """Muestra un resumen de la conversación que se va a continuar."""
    print(f"\n{'='*50}")
    print("📊 RESUMEN DE LA CONVERSACIÓN")
    print("="*50)
    
    # Obtener resumen básico
    resumen = get_session_summary(session_id)
    if resumen:
        print(f"🔹 Total de intercambios: {resumen['total_turns']}")
        print(f"🔹 Inicio: {resumen['session_start'].strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"🔹 Última actividad: {resumen['session_end'].strftime('%d/%m/%Y %H:%M:%S')}")
        if resumen['duration_minutes'] > 0:
            print(f"🔹 Duración total: {resumen['duration_minutes']:.1f} minutos")
    
    # Mostrar últimos intercambios
    turnos = get_conversation_by_session_id(session_id)
    if turnos:
        print(f"\n📝 Últimos intercambios:")
        print("-"*50)
        
        # Mostrar solo los últimos 3 intercambios
        ultimos_turnos = turnos[-3:] if len(turnos) > 3 else turnos
        
        for i, turno in enumerate(ultimos_turnos, 1):
            print(f"\n🔹 Intercambio #{len(turnos) - len(ultimos_turnos) + i}")
            print(f"👤 Usuario: {turno['user_prompt']}")
            respuesta_corta = turno['ai_response'][:100] + '...' if len(turno['ai_response']) > 100 else turno['ai_response']
            print(f"🤖 Asistente: {respuesta_corta}")
    
    print("="*50)

def iniciar_continuacion_conversacion(session_id: str):
    """Inicia la continuación de una conversación existente."""
    global is_conversation_active, current_session_id
    
    print(f"\n🚀 Continuando conversación...")
    is_conversation_active = True
    current_session_id = session_id
    session_short = session_id[:8]
    
    # Seleccionar modelo
    modelo_seleccionado = seleccionar_modelo()
    print(f"✅ Modelo seleccionado: {modelo_seleccionado.capitalize()}")
    
    print("\n" + "="*60)
    print("🔄 CONTINUANDO CONVERSACIÓN")
    print("="*60)
    print(f"📝 ID de sesión: {session_short}...")
    print("🧠 El asistente tiene acceso a todo el historial de esta conversación")
    print("💡 Puedes hacer preguntas que se refieran a intercambios anteriores")
    print("🔍 Escribe 'contexto' para ver el historial reciente")
    print("💡 Escribe 'salir', 'exit' o 'quit' para volver al menú principal")
    print("-"*60)
    
    while True:
        pregunta = input("\n👤 Tú: ").strip()
        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("\n🔙 Conversación pausada. Volviendo al menú principal...")
            is_conversation_active = False
            break

        if not pregunta:
            print("⚠️  Pregunta vacía. Por favor, escribe algo.")
            continue

        # Comando especial para ver el contexto
        if pregunta.lower() in ["contexto", "historial", "ver contexto"]:
            mostrar_contexto_actual()
            continue

        manejar_pregunta(pregunta, modelo_seleccionado)

if __name__ == "__main__":
    main()
