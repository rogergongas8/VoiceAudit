import json
from src.conexion_db import ConexionDB

class AuthDAO:
    def __init__(self):
        self.db = ConexionDB()

    def registrar_usuario(self, username, passphrase):
        sql = """
            INSERT INTO usuarios_voz (username, passphrase_text) 
            VALUES (%s, %s) RETURNING id;
        """
        try:
            conn = self.db.connection
            with conn.cursor() as cursor:
                cursor.execute(sql, (username, passphrase))
                user_id = cursor.fetchone()[0]
                conn.commit()
                return user_id
        except Exception as e:
            conn.rollback()
            print(f"Error registrando usuario: {e}")
            return None

    def obtener_usuario(self, username):
        sql = "SELECT id, passphrase_text, intentos_fallidos FROM usuarios_voz WHERE username = %s;"
        with self.db.connection.cursor() as cursor:
            cursor.execute(sql, (username,))
            return cursor.fetchone()

    def registrar_log(self, usuario_id, datos_dict):
        sql = """
            INSERT INTO log_accesos_voz (usuario_id, resultado_json) 
            VALUES (%s, %s);
        """
        json_data = json.dumps(datos_dict)  # Convierte dict a JSON string
        
        try:
            conn = self.db.connection
            with conn.cursor() as cursor:
                cursor.execute(sql, (usuario_id, json_data))
                conn.commit()
        except Exception as e:
            print(f"Error guardando log JSONB: {e}")

    def obtener_auditoria_critica(self):
        sql = """
            SELECT u.username, l.resultado_json 
            FROM log_accesos_voz l
            JOIN usuarios_voz u ON l.usuario_id = u.id
            WHERE l.resultado_json->>'status' = 'FAIL' 
            OR (l.resultado_json->>'confianza')::float < 0.6
            ORDER BY l.fecha_intento DESC;
        """
        with self.db.connection.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()