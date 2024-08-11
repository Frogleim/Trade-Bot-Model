import psycopg2


class DataBase:
    def __init__(self):
        self.user = "postgres"
        self.password = "admin"
        self.host = "pgdb"
        self.port = 5433
        self.database = "miya"

    def connect(self):
        return psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )

    def create_all_tables(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS signals (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(50) NOT NULL,
        signal VARCHAR(10) NOT NULL,
        entry_price NUMERIC(18, 8),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
            """
        )

        print('Table signals created successfully')
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS binance_keys (
        id SERIAL PRIMARY KEY,
        api_key VARCHAR,
        api_secret VARCHAR
);
            """
        )
        print('Table binance_keys created successfully')
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS trade_coins (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR,
        quantity INT,
        checkpoints FLOAT8[]
);
            """
        )
        print('Table trade_coins created successfully')
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS trades_alert (
        id SERIAL PRIMARY KEY,
        is_finished VARCHAR
);
            """
        )
        print('Table trades_alert created successfully')
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS trades_history (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR,
        entry_price VARCHAR,
        exit_price VARCHAR,
        profit VARCHAR
);
            """
        )
        print('Table trades_alert created successfully')
        print('All tables created...')
        conn.commit()

    def clean_db(self, table_name):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()

    def clean_signals(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM signals")
        conn.commit()

    def get_trade_settings(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trade_coins")
        rows = cursor.fetchall()
        return rows

    def insert_signal(self, symbol, entry_price, signal, indicator):
        conn = self.connect()
        cursor = conn.cursor()
        self.clean_signals()
        cursor.execute("INSERT INTO signals (coin, signal, entry_price, indicator)"
                       " VALUES (%s, %s, %s, %s)",
                       (symbol, signal, entry_price, indicator))
        conn.commit()

    def insert_binance_keys(self, api_key, api_secret):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO binance_keys (api_key, api_secret) VALUES (%s, %s)", (api_key, api_secret))
        conn.commit()

    def insert_trades_coins(self, symbol, quantity, checkpoints, stop_loss, indicator):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO trade_coins (symbol, quantity, checkpoints, stop_loss, indicator)"
                       f" VALUES (%s, %s, %s, %s, %s)", (symbol, quantity, checkpoints, stop_loss, indicator))
        conn.commit()

    def get_signal(self, symbol):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM signals WHERE coin='{symbol}'")
        rows = cursor.fetchall()
        print(len(rows))
        if len(rows) > 0:
            return rows[-1]
        else:
            return None

    def check_is_finished(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM trades_alert ")
        rows = cursor.fetchall()
        if len(rows) > 0:
            return True
        else:
            return False

    def get_binance_keys(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT api_key, api_secret FROM binance_keys")
        row = cursor.fetchone()

        cursor.close()
        conn.close()
        if row:
            api_key = row[0]
            api_secret = row[1]
            return api_key, api_secret
        return None

    def get_trade_coins(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trade_coins")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        symbol = row[1]
        quantity = row[2]
        checkpoints = row[3]
        return symbol, quantity, checkpoints

    def get_trade_settings(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trade_coins")
        rows = cursor.fetchall()
        return rows

    def get_trade_history(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades_history")
        rows = cursor.fetchall()
        return rows

    def update_trade_coins(self, column, update_value, indicator):
        conn = self.connect()
        cursor = conn.cursor()
        query = f"UPDATE trade_coins SET {column} =%s WHERE indicator=%s;"
        cursor.execute(query, (update_value, indicator))
        conn.commit()


    def get_trade_history(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades_history")
        rows = cursor.fetchall()
        return rows


if __name__ == '__main__':
    symbol = 'MATICUSDT'
    db = DataBase()
    rows = db.get_trade_history()
    print(rows)
