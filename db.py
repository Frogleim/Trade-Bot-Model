import psycopg2


class DataBase:
    def __init__(self):
        self.user = "postgres"
        self.password = "admin"
        self.host = "localhost"
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
        indicator VARCHAR,
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
        checkpoints FLOAT8[],
        stop_loss numeric,
        indicator VARCHAR
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
        profit VARCHAR,
        indicator VARCHAR
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

    def insert_signal(self, symbol, entry_price, signal, indicator):
        conn = self.connect()
        cursor = conn.cursor()
        self.clean_db(table_name='signals')
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
        cursor.execute(f"INSERT INTO trade_coins (symbol, quantity, checkpoints, stop_loss) VALUES (%s, %s, %s, %s)",
                       (symbol, quantity, checkpoints, stop_loss))
        conn.commit()

    def get_signal(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM signals")
        rows = cursor.fetchall()
        print(len(rows))
        if len(rows) > 0:
            return rows[-1]
        else:
            return None

    def check_is_finished(self):
        while True:
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

    def get_trade_coins(self, indicator):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trade_coins WHERE indicator=%s", (indicator,))
        row = cursor.fetchall()
        print(row)
        cursor.close()
        conn.close()

        return row[0]

    def insert_test_signals(self, close, sma21, up_trigger_zone, down_trigger_zone, buy_signal, sell_signal,
                            state):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
    INSERT INTO test_signals (close, sma21, up_trigger_zone, down_trigger_zone, buy_signal, sell_signal, state)
    VALUES (%s, %s, %s,  %s, %s, %s, %s)
"""
        cursor.execute(
            query,
            (
                close,
                sma21,
                up_trigger_zone,
                down_trigger_zone,
                buy_signal,
                sell_signal,
                state
            )
        )

        conn.commit()
        cursor.close()
        conn.close()


if __name__ == '__main__':
    symbol = 'MATICUSDT'
    db = DataBase()
    rows = db.get_trade_coins('SMA21')
    print(rows)
