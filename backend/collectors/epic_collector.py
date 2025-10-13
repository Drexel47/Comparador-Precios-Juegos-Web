import requests
import mysql.connector
from datetime import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import MYSQL_CONFIG  # Usa la misma configuración que tus otros collectors
from collectors.utils.currency_converter import get_usd_to_clp

def guardar_en_bd(nombre, precio, moneda, tienda="Epic Games"):
    """Guarda o actualiza el juego y su precio en la base de datos."""
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cur = conn.cursor()

    slug = nombre.lower().replace(' ', '-')
    # Inserta el juego si no existe
    cur.execute("INSERT IGNORE INTO juegos (nombre, slug) VALUES (%s, %s)", (nombre, slug))
    conn.commit()

    # Obtiene el ID del juego
    cur.execute("SELECT id FROM juegos WHERE nombre = %s", (nombre,))
    juego_id = cur.fetchone()[0]

    # Conversión automática si viene en USD
    if tienda.lower() == 'epic games' and moneda.upper() == 'USD':
        tasa = get_usd_to_clp()
        precio_clp = round(precio * tasa)
        moneda = 'CLP'
        print(f"[INFO] Convertido {precio} USD → {precio_clp} CLP")
        precio = precio_clp




    # Inserta el precio actual
    cur.execute("""
        INSERT INTO precios (juego_id, tienda, precio, moneda, fecha)
        VALUES (%s, %s, %s, %s, %s)
    """, (juego_id, tienda, precio, moneda, datetime.utcnow()))
    conn.commit()

    cur.close()
    conn.close()


def obtener_juegos_epic():
    """Obtiene el listado actual de juegos de Epic Games (incluye precios y promociones)."""
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("Error al obtener datos de Epic Games:", e)
        return []

    juegos = []
    catalog = data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])

    for juego in catalog:
        nombre = juego.get('title')
        price_info = juego.get('price', {}).get('totalPrice', {})
        precio_bruto = price_info.get('discountPrice', 0)
        moneda = price_info.get('currencyCode', 'USD')

        # Los precios vienen en centavos
        precio = precio_bruto / 100 if isinstance(precio_bruto, int) else 0.0

        if nombre and precio >= 0:
            juegos.append({
                'nombre': nombre.strip(),
                'precio': precio,
                'moneda': moneda
            })

    return juegos


def main():
    print("🔄 Obteniendo datos de Epic Games...")
    juegos = obtener_juegos_epic()
    print(f"Se encontraron {len(juegos)} juegos en el catálogo de Epic Games.")

    if not juegos:
        return

    for juego in juegos:
        try:
            guardar_en_bd(juego['nombre'], juego['precio'], juego['moneda'])
        except Exception as e:
            print(f"Error guardando {juego['nombre']}: {e}")

    print("Sincronización de precios de Epic Games completada.")


if __name__ == "__main__":
    main()