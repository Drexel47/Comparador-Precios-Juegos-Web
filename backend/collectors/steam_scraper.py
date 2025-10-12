import requests
import mysql.connector
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import MYSQL_CONFIG

def obtener_juegos_steam(cc='cl', lang='spanish'):
    """
    Obtiene una lista de juegos populares con precio desde la API de Steam (sin requerir API Key).
    """
    try:
        # Endpoint de juegos destacados (gratis y de pago)
        url = f"https://store.steampowered.com/api/featuredcategories/?cc={cc}&l={lang}"
        r = requests.get(url, timeout=15)
        r.raise_for_status()

        data = r.json()
        juegos = []

        # Extraemos algunos juegos destacados (action, top sellers, etc.)
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

def guardar_juego(nombre, precio, moneda, tienda='Steam'):
    """
    Inserta o actualiza los datos del juego y su precio.
    """
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cur = conn.cursor()
    slug = nombre.lower().replace(' ', '-')

    cur.execute("INSERT IGNORE INTO juegos (nombre, slug) VALUES (%s, %s)", (nombre, slug))
    conn.commit()

    cur.execute("SELECT id FROM juegos WHERE nombre = %s", (nombre,))
    result = cur.fetchone()
    if not result:
        cur.close()
        conn.close()
        return
    juego_id = result[0]

    cur.execute(
        "INSERT INTO precios (juego_id, tienda, precio, moneda) VALUES (%s, %s, %s, %s)",
        (juego_id, tienda, precio, moneda)
    )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    juegos = obtener_juegos_steam()
    print(f"Se obtuvieron {len(juegos)} juegos.")

    for j in juegos:
        guardar_juego(j['nombre'], j['precio'], j['moneda'])
        print(f"Guardado: {j['nombre']} - {j['precio']} {j['moneda']}")