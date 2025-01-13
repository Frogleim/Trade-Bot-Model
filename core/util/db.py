import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='../.env')

def connect_to_postgresql():
    """
    Establishes a connection to a PostgreSQL database.
    Returns the connection and cursor objects.
    """
    try:
        # Database credentials from environment variables
        db_name = "miya"
        db_user = "postgres"
        db_password = "admin"
        db_host = "localhost"
        db_port = os.environ.get('DB_PORT', 5433)

        # Establish connection
        connection = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )

        cursor = connection.cursor()
        print("Connected to PostgreSQL database successfully.")
        return connection, cursor

    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None, None

def close_postgresql_connection(connection, cursor):
    """
    Closes the PostgreSQL database connection and cursor.
    """
    try:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("PostgreSQL connection closed.")
    except Exception as e:
        print(f"Error closing PostgreSQL connection: {e}")

def insert_history(symbol, entry_price, close_price, pnl, side):
    """
    Inserts trade history into the PostgreSQL database.
    Parameters:
    - entry_price: The entry price of the trade.
    - close_price: The closing price of the trade.
    - pnl: Profit and loss for the trade.
    - side: Trade side ('Long' or 'Short').
    """
    conn, cur = connect_to_postgresql()
    if not conn or not cur:
        print("Failed to insert trade history: Database connection issue.")
        return

    try:
        # Create the trade history table if it doesn't exist
        cur.execute('''
            CREATE TABLE IF NOT EXISTS trades_history (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR,
                entry_price VARCHAR,
                exit_price VARCHAR,
                profit VARCHAR
                
            );
        ''')

        # Insert trade history record
        cur.execute(
            '''INSERT INTO trades_history (symbol, entry_price, exit_price, profit) VALUES (%s, %s, %s, %s)''',
            (symbol, entry_price, close_price, pnl, )
        )

        conn.commit()
        print("Trade history inserted successfully.")

    except Exception as e:
        print(f"Error inserting trade history: {e}")
        conn.rollback()

    finally:
        close_postgresql_connection(conn, cur)

# Example usage
if __name__ == "__main__":
    # Example insert
    insert_history(symbol='BTCUSDT', entry_price=30000, close_price=30500, pnl=500, side='Long')
