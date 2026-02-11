import json
from src.conexion_db import ConexionDB

class AuthDAO:
    def __init__(self):
        self.db = ConexionDB()

    def registrar_usuario(self, username, passphrase):
        """Inserta usuario y devuelve su ID"""
        sql = """
            INSERT INTO usuarios_voz (username, passphrase_text) 
            VALUES (%s, %s) RETURNING id;
        """
        conn = None
        try:
            conn = self.db.connection
            with conn.cursor() as cursor:
                cursor.execute(sql, (username, passphrase))
                user_id = cursor.fetchone()[0]
                conn.commit()  # <--- IMPORTANTE: Confirma el guardado
                print(f">> ÉXITO SQL: Usuario '{username}' guardado con ID {user_id}")
                return user_id
        except Exception as e:
            if conn: conn.rollback()
            print(f">> ERROR SQL (Usuario): {e}")
            return None

    def obtener_usuario(self, username):
        """Busca un usuario por nombre"""
        sql = "SELECT id, passphrase_text, intentos_fallidos FROM usuarios_voz WHERE username = %s;"
        try:
            cursor = self.db.get_cursor()
            cursor.execute(sql, (username,))
            return cursor.fetchone()
        except Exception as e:
            print(f">> ERROR SQL (Buscar Usuario): {e}")
            return None

    def registrar_log(self, usuario_id, datos_dict):
        """Guarda el JSONB"""
        sql = """
            INSERT INTO log_accesos_voz (usuario_id, resultado_json) 
            VALUES (%s, %s);
        """
        json_data = json.dumps(datos_dict)
        conn = None
        try:
            conn = self.db.connection
            with conn.cursor() as cursor:
                cursor.execute(sql, (usuario_id, json_data))
                conn.commit() # <--- IMPORTANTE
                print(f">> ÉXITO SQL: Log guardado para usuario {usuario_id}")
        except Exception as e:
            if conn: conn.rollback()
            print(f">> ERROR SQL (Log): {e}")

    def obtener_auditoria_critica(self):
        """Consulta logs fallidos"""
        sql = """
            SELECT u.username, l.resultado_json 
            FROM log_accesos_voz l
            JOIN usuarios_voz u ON l.usuario_id = u.id
            WHERE l.resultado_json->>'status' = 'FAIL' 
            OR (l.resultado_json->>'confianza')::float < 0.6
            ORDER BY l.fecha_intento DESC;
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f">> ERROR SQL (Auditoría): {e}")
            return []