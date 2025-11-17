from flask import Flask
import redis
import os
import psycopg2

app = Flask(__name__)

# Redis config (optional—comment out if not using Redis)
redis_host = os.getenv('REDIS_HOST', 'redis')
cache = redis.Redis(host=redis_host, port=6379)

# Postgres config
db_host = os.getenv('DATABASE_HOST', 'db')
db_name = os.getenv('DATABASE_NAME', 'mydb')
db_user = os.getenv('DATABASE_USER', 'myuser')
db_password = os.getenv('DATABASE_PASSWORD', 'mypassword')

def get_conn():
    return psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

@app.route('/')
def hello():
    # Increment Redis hits
    try:
        cache_count = cache.incr('hits')
    except Exception as e:
        cache_count = f"Redis error: {e}"

    # Connect to Postgres and update visit count
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS visits (id SERIAL PRIMARY KEY, count INTEGER);")
            cur.execute("SELECT count FROM visits WHERE id=1;")
            row = cur.fetchone()
            if row is None:
                cur.execute("INSERT INTO visits (id, count) VALUES (1, 1);")
                visit_count = 1
            else:
                visit_count = row[0] + 1
                cur.execute("UPDATE visits SET count=%s WHERE id=1;", (visit_count,))
            conn.commit()
        conn.close()
    except Exception as e:
        visit_count = f"Postgres error: {e}"

    return (
        f"Hello! This page has been visited {visit_count} times (tracked in Postgres), "
        f"and Redis cached hits: {cache_count}"
    )

@app.route('/login')
def login():
    return "Login page coming soon!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
