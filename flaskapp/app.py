from flask import Flask
from flaskext.mysql import MySQL
import os
import time

app = Flask(__name__)

# MySQL Configuration from Environment Variables
app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST', 'db-service')
app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_DATABASE_USER', 'root')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD', 'root')
app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE_DB', 'BucketList')

mysql = MySQL()
mysql.init_app(app)


# Retry DB Connection
def get_db_connection():
    retries = 10

    while retries > 0:
        try:
            conn = mysql.connect()
            return conn
        except Exception as e:
            print(f"MySQL connection failed: {e}")
            retries -= 1
            time.sleep(5)

    return None


@app.route('/')
def home():
    conn = get_db_connection()

    if conn is None:
        return "Failed to connect to MySQL database"

    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255)
        )
    """)

    # Insert sample data
    cursor.execute("""
        INSERT INTO items(name)
        VALUES ('Kubernetes Flask App')
    """)

    conn.commit()

    # Read data
    cursor.execute("SELECT * FROM items")

    rows = cursor.fetchall()

    result = "<h1>Flask + MySQL on Kubernetes</h1>"

    for row in rows:
        result += f"<p>ID: {row[0]} | Name: {row[1]}</p>"

    cursor.close()
    conn.close()

    return result


@app.route('/health')
def health():
    return "OK", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)