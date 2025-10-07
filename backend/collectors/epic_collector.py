import requests, mysql.connector
from config import MYSQL_CONFIG

def buscar_por_titulo(title_query):
    url='https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions'
    r=requests.get(url, timeout=15)
    r.raise_for_status()
    data=r.json().get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])
    for g in data:
        if title_query.lower() in g.get('title','').lower():
            price=g.get('price', {}).get('totalPrice', {})
            return {
                'nombre': g.get('title'),
                'precio': price.get('discountPrice') or price.get('originalPrice', 0),
                'moneda': price.get('currencyCode','USD')
            }
    return None
