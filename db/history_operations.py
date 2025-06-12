import pyodbc
from db.connection import get_connection

def save_conversation(user_prompt: str, ai_response: str):
    """Saves a conversation to the database."""
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            sql = "INSERT INTO conversation_history (user_prompt, ai_response) VALUES (?, ?)"
            cursor.execute(sql, user_prompt, ai_response)
            conn.commit()
            print("✅ Conversation saved successfully.")
            cursor.close()
            conn.close()
        else:
            print("⚠️ Could not connect to the database to save conversation.")
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"❌ Error saving conversation: {sqlstate}")
        print(ex)
    except Exception as e:
        print(f"❌ An unexpected error occurred while saving conversation: {e}")

def get_all_conversations() -> list:
    """Retrieves all conversations from the database, ordered by timestamp descending."""
    conversations = []
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            # Order by ID descending as it's an IDENTITY column, which implies order of insertion
            sql = "SELECT id, timestamp, user_prompt, ai_response FROM conversation_history ORDER BY id DESC"
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                conversations.append({
                    "id": row.id,
                    "timestamp": row.timestamp,
                    "user_prompt": row.user_prompt,
                    "ai_response": row.ai_response
                })
            cursor.close()
            conn.close()
        else:
            print("⚠️ Could not connect to the database to retrieve conversations.")
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"❌ Error retrieving conversations: {sqlstate}")
        print(ex)
    except Exception as e:
        print(f"❌ An unexpected error occurred while retrieving conversations: {e}")
    return conversations

def get_conversation_by_id(conversation_id: int) -> dict | None:
    """Retrieves a specific conversation by its ID."""
    conversation = None
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            sql = "SELECT id, timestamp, user_prompt, ai_response FROM conversation_history WHERE id = ?"
            cursor.execute(sql, conversation_id)
            row = cursor.fetchone()
            if row:
                conversation = {
                    "id": row.id,
                    "timestamp": row.timestamp,
                    "user_prompt": row.user_prompt,
                    "ai_response": row.ai_response
                }
            cursor.close()
            conn.close()
        else:
            print("⚠️ Could not connect to the database to retrieve conversation.")
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"❌ Error retrieving conversation by ID: {sqlstate}")
        print(ex)
    except Exception as e:
        print(f"❌ An unexpected error occurred while retrieving conversation by ID: {e}")
    return conversation
