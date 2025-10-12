from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from config import MYSQL_CONFIG

app = Flask(__name__)
CORS(app)
def get_connection():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Error as e:
        print(f"Hubo problemas al conectar a la base de datos: {e}")
        return None

@app.route('/api/games')
def list_games():
    conn = get_connection()
    if not conn:
        return jsonify({'error':'Conexión fallida con la base de datos.'}), 500
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT id, nombre, slug FROM juegos ORDER BY nombre')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/prices')
def get_prices():
    game_id = request.args.get('game_id')
    if not game_id:
        return jsonify({'error':'missing game_id'}), 400
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT tienda, precio, moneda, fecha FROM precios WHERE juego_id = %s ORDER BY fecha DESC', (game_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
