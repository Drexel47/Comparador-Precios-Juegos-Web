import requests, mysql.connector
from config import MYSQL_CONFIG

def obtener_precio_steam(appid: str, cc='cl', lang='spanish'):
    url='https://store.steampowered.com/api/appdetails'
    r=requests.get(url, params={'appids': appid, 'cc':cc, 'l':lang}, timeout=15)
    r.raise_for_status()
    data=r.json().get(appid, {}).get('data', {})
    price=data.get('price_overview') or {}
    return {
        'nombre': data.get('name'),
        'precio': price.get('final', 0)/100,
        'moneda': price.get('currency', 'CLP')
    }

def guardar(nombre, precio, moneda, tienda='Steam'):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cur = conn.cursor()
    slug = nombre.lower().replace(' ','-')
    cur.execute("INSERT IGNORE INTO juegos (nombre, slug) VALUES (%s,%s)", (nombre, slug))
    conn.commit()
    cur.execute("SELECT id FROM juegos WHERE nombre=%s", (nombre,))
    juego_id = cur.fetchone()[0]
    cur.execute("INSERT INTO precios (juego_id, tienda, precio, moneda) VALUES (%s,%s,%s,%s)", (juego_id, tienda, precio, moneda))
    conn.commit()
    cur.close()
    conn.close()

if __name__=='__main__':
    appid='730'
    try:
        datos=obtener_precio_steam(appid)
        if datos and datos['nombre']:
            guardar(datos['nombre'], datos['precio'], datos['moneda'])
            print('Guardado', datos)
    except Exception as e:
        print('Error', e)
