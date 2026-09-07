import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def create_market_prices_table():
    create_table_query = """
        CREATE TABLE IF NOT EXISTS market_prices (
            id BIGSERIAL PRIMARY KEY,
            recorded_at TIMESTAMPTZ NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            price NUMERIC(20, 8) NOT NULL,
            bid NUMERIC(20, 8) NOT NULL,
            ask NUMERIC(20, 8) NOT NULL,
            spread NUMERIC(20, 8) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)

        connection.commit()

    print("Table created successfully: market_prices")

def test_connection():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user;")
            result = cursor.fetchone()

    print(f"Connected to database: {result[0]}")
    print(f"Connected as user: {result[1]}")


if __name__ == "__main__":
    test_connection()
    create_market_prices_table()