import requests
import mysql.connector
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import MYSQL_CONFIG

def obtener_juegos_steam(cc='cl', lang='spanish'):
    """
    Obtiene una lista de juegos populares con precio desde la API pública de Steam.
    """
    try:
        url = f"https://store.steampowered.com/api/featuredcategories/?cc={cc}&l={lang}"
        r = requests.get(url, timeout=15)
        r.raise_for_status()

        data = r.json()
        juegos = []

        for categoria in ['topsellers', 'new_releases', 'specials']:
            for j in data.get(categoria, {}).get('items', []):
                juegos.append({
                    'appid': j.get('id'),
                    'nombre': j.get('name'),
                    'precio': (j.get('final_price') or 0) / 100,
                    'moneda': j.get('currency', 'CLP'),
                })

        return juegos

    except Exception as e:
        print('Error obteniendo juegos:', e)
        return []

def guardar_juego(cur, conn, nombre, precio, moneda, tienda='Steam'):
    """
    Inserta o actualiza los datos del juego y su precio usando un cursor existente.
    """
    slug = nombre.lower().replace(' ', '-')

    # --- Insertar el juego si no existe ---
    cur.execute(
        "INSERT IGNORE INTO juegos (nombre, slug) VALUES (%s, %s)",
        (nombre, slug)
    )

    #limpiar cualquier resultado pendiente
    try:
        while cur.next_result():
            pass
    except:
        pass

    # --- Buscar ID del juego ---
    cur.execute("SELECT id FROM juegos WHERE nombre = %s", (nombre,))
    result = cur.fetchone()
    if not result:
        print(f"⚠️ No se encontró el juego '{nombre}'")
        return
    juego_id = result[0]

    # --- Insertar o actualizar el precio ---
    cur.execute(
        "INSERT INTO precios (juego_id, tienda, precio, moneda) VALUES (%s, %s, %s, %s)",
        (juego_id, tienda, precio, moneda)
    )

    # Limpieza por seguridad
    try:
        while cur.next_result():
            pass
    except:
        pass


def main():
    try:
        #Abrir una sola conexión para todos los juegos
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cur = conn.cursor(buffered=True)

        juegos = obtener_juegos_steam()
        print(f"Se obtuvieron {len(juegos)} juegos.")

        for j in juegos:
            try:
                guardar_juego(cur, conn, j['nombre'], j['precio'], j['moneda'])
                conn.commit()  # commit después de cada inserción
                print(f"Guardado: {j['nombre']} - {j['precio']} {j['moneda']}")
            except Exception as e:
                print(f"Error guardando '{j['nombre']}': {e}")

    except mysql.connector.Error as e:
        print("Error al conectar con MySQL:", e)

    finally:
        if 'cur' in locals():
            try:
                cur.close()
            except:
                pass

        if 'conn' in locals() and conn.is_connected():
            conn.close()

        


if __name__ == '__main__':
    main()
