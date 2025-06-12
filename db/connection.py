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
