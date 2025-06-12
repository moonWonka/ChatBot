import pyodbc
from db.connection import get_connection
import uuid

def generate_session_id() -> str:
    """Generates a unique session ID."""
    return str(uuid.uuid4())

def save_conversation(user_prompt: str, ai_response: str, session_id: str):
    """Saves a conversation to the database."""
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            sql = "INSERT INTO conversation_history (user_prompt, ai_response, session_id) VALUES (?, ?, ?)"
            cursor.execute(sql, user_prompt, ai_response, session_id)
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
    """Retrieves all unique conversation sessions from the database, showing the first prompt of each."""
    sessions = []
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            sql = """
            WITH RankedConversations AS (
                SELECT
                    session_id,
                    user_prompt,
                    timestamp,
                    ROW_NUMBER() OVER(PARTITION BY session_id ORDER BY id ASC) as rn
                FROM conversation_history
            )
            SELECT
                session_id,
                user_prompt,
                timestamp
            FROM RankedConversations
            WHERE rn = 1
            ORDER BY timestamp DESC;
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                sessions.append({
                    "session_id": row.session_id,
                    "first_user_prompt": row.user_prompt,
                    "timestamp": row.timestamp
                })
            cursor.close()
            conn.close()
        else:
            print("⚠️ Could not connect to the database to retrieve conversation sessions.")
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"❌ Error retrieving conversation sessions: {sqlstate}")
        print(ex)
    except Exception as e:
        print(f"❌ An unexpected error occurred while retrieving conversation sessions: {e}")
    return sessions

def get_conversation_by_session_id(session_id: str) -> list:
    """Retrieves all turns for a specific conversation session ID, ordered by timestamp."""
    conversation_turns = []
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            sql = "SELECT id, timestamp, user_prompt, ai_response FROM conversation_history WHERE session_id = ? ORDER BY id ASC"
            cursor.execute(sql, session_id)
            rows = cursor.fetchall()
            for row in rows:
                conversation_turns.append({
                    "id": row.id,
                    "timestamp": row.timestamp,
                    "user_prompt": row.user_prompt,
                    "ai_response": row.ai_response
                })
            cursor.close()
            conn.close()
        else:
            print("⚠️ Could not connect to the database to retrieve conversation details.")
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"❌ Error retrieving conversation details by session ID: {sqlstate}")
        print(ex)
    except Exception as e:
        print(f"❌ An unexpected error occurred while retrieving conversation details by session ID: {e}")
    return conversation_turns
