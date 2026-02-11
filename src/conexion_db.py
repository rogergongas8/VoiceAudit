import psycopg2
from src.config import Config

class ConexionDB:
    _instancia = None 

    def __new__(cls):
        if cls._instancia is None:
            try:
                cls._instancia = super(ConexionDB, cls).__new__(cls)
                cls._instancia.connection = psycopg2.connect(
                    host=Config.DB_HOST,
                    database=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASS,
                    port=Config.DB_PORT
                )
                print(">> Conexión Singleton establecida.")
            except Exception as e:
                print(f"Error crítico de conexión: {e}")
                cls._instancia = None
        return cls._instancia

    def get_cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()
        
    def close(self):
        if self.connection:
            self.connection.close()
            ConexionDB._instancia = None