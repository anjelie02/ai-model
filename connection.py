
import psycopg2
def get_connection():
    try:
        return psycopg2.connect(
            database="shopify-reporting-app",
            user="postgres",
            password="Sairam_12345",
            host="localhost",
            port=5432,
        )
    except:
        return False
conn = get_connection()
if conn:
    print("Connection to the PostgreSQL established successfully.")
else:
    print("Connection to the PostgreSQL encountered and error.")