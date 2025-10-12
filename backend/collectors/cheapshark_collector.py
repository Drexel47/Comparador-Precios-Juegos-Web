import requests
import mysql.connector

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import MYSQL_CONFIG

# API base de CheapShark
API_URL = "https://www.cheapshark.com/api/1.0"

# Tasa de cambio (USD a CLP) — puedes actualizarla con otra API si quieres
USD_TO_CLP = 950


def obtener_juego_por_nombre(nombre):
    """Busca un juego por nombre en CheapShark"""
    r = requests.get(f"{API_URL}/games", params={"title": nombre}, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data:
        return None
    # Retorna el primer resultado
    return data[0]


def obtener_precios_por_juego(game_id):
    """Obtiene todas las ofertas del juego (Steam, Epic, etc.)"""
    r = requests.get(f"{API_URL}/games", params={"id": game_id}, timeout=10)
    r.raise_for_status()
    data = r.json()
    deals = data.get("deals", [])
    return [
        {
            "store": d["storeID"],
            "precio_usd": float(d["price"]),
            "precio_clp": round(float(d["price"]) * USD_TO_CLP, 0),
            "url": f"https://www.cheapshark.com/redirect?dealID={d['dealID']}",
        }
        for d in deals
    ]


def guardar(nombre, precios):
    """Guarda el juego y sus precios en MySQL"""
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cur = conn.cursor()
    slug = nombre.lower().replace(" ", "-")
    cur.execute("INSERT IGNORE INTO juegos (nombre, slug) VALUES (%s,%s)", (nombre, slug))
    conn.commit()
    cur.execute("SELECT id FROM juegos WHERE nombre=%s", (nombre,))
    juego_id = cur.fetchone()[0]

    for p in precios:
        cur.execute("""
            INSERT INTO precios (juego_id, tienda, precio, moneda, fecha)
            VALUES (%s, %s, %s, %s, NOW())
        """, (juego_id, p["store"], p["precio_clp"], "CLP"))

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    try:
        nombre = "Cyberpunk 2077"
        juego = obtener_juego_por_nombre(nombre)
        if juego:
            precios = obtener_precios_por_juego(juego["gameID"])
            guardar(nombre, precios)
            print(f"Guardado: {nombre} ({len(precios)} ofertas)")
        else:
            print("Juego no encontrado.")
    except Exception as e:
        print("Error:", e)
