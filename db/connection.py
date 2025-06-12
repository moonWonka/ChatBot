import pyodbc
from config.settings import DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD

DRIVER = '{ODBC Driver 18 for SQL Server}'

def get_connection():
    """Obtiene una conexión a la base de datos"""
    try:
        connection_string = f"""
            DRIVER={DRIVER};
            SERVER={DB_SERVER};
            DATABASE={DB_NAME};
            UID={DB_USER};
            PWD={DB_PASSWORD};
            Encrypt=yes;
            TrustServerCertificate=no;
            Connection Timeout=30;
        """
        connection = pyodbc.connect(connection_string)
        return connection
    except Exception as e:
        print("❌ Error al conectar a la base de datos:", e)
        return None


def execute_query(sql_query: str) -> list:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        if not conn:
            print("❌ Error: Could not establish database connection for query execution.")
            return []

        cursor = conn.cursor()
        # print(f"Executing query: {sql_query}") # Temporary print for debugging, can be removed later
        cursor.execute(sql_query)

        # Check if the query produces results (e.g., SELECT)
        if cursor.description: # Not None if it's a SELECT like statement
            results = cursor.fetchall()
            # Convert Row objects to dictionaries for easier use
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in results]
        else: # For INSERT, UPDATE, DELETE, etc., that don't return rows this way
            conn.commit() # Important for modifications
            return [] # Or return a success message or row count if appropriate

    except pyodbc.Error as ex:
        # sqlstate = ex.args[0] # This might not always be available or be the most useful part
        print(f"❌ Database error during query execution: {ex}")
        # Consider rolling back if it was a transactional error.
        return []
    except Exception as e:
        print(f"❌ An unexpected error occurred during query execution: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
