from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import pool

app = Flask(__name__)
CORS(app)

# PostgreSQL connection pool
db_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    database="drone_db",
    user="postgres",
    password="enter6.",  # Replace with your postgres password
    host="localhost",
    port="5432"
)

@app.route('/api/drones', methods=['GET'])
def get_drones():
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, model, latitude, longitude FROM drones")
            drones = cur.fetchall()
            return jsonify([{
                'id': row[0],
                'name': row[1],
                'model': row[2],
                'latitude': float(row[3]),
                'longitude': float(row[4])
            } for row in drones])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db_pool.putconn(conn)

if __name__ == '__main__':
    app.run(debug=True)