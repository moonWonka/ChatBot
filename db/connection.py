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
    try:
        conn = get_connection()
        if not conn:
            print("❌ Error: Could not establish database connection for query execution.")
            return []

        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    except Exception as e:
        print(f"❌ Error during query execution: {e}")
        return []
