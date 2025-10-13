import requests

USD_TO_CLP_RATE = None

def get_usd_to_clp():
    """
    Obtiene la tasa actual de conversión USD → CLP desde open.er-api.com
    """
    global USD_TO_CLP_RATE
    if USD_TO_CLP_RATE is not None:
        return USD_TO_CLP_RATE  # usa el cache si ya fue cargado

    url = "https://open.er-api.com/v6/latest/USD"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        rate = data.get('rates', {}).get('CLP')
        if rate:
            USD_TO_CLP_RATE = rate
            print(f"[INFO] Tasa USD→CLP actual: {rate}")
            return rate
        else:
            raise ValueError("No se encontró la tasa CLP en la respuesta.")
    except Exception as e:
        print("[ERROR] No se pudo obtener la tasa USD→CLP:", e)
        return 950.0  # valor fallback aproximado