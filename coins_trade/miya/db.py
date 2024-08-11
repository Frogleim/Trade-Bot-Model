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

    def clean_db(self, table_name):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()

    def insert_test_trades(self, symbol, entry_price, close_price, pnl, indicator, is_profit=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO trades_history (symbol, entry_price, exit_price, profit, indicator)"
                       "VALUES (%s, %s, %s, %s, %s)",
                       (symbol, entry_price, close_price, pnl, indicator))
        self.insert_is_finished()
        conn.commit()



    def insert_is_finished(self):
        is_finished = 'yes'
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO trades_alert (is_finished) VALUES (%s)", (is_finished,))
            conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.rollback()  # Rollback in case of error
        finally:
            cursor.close()  # Close the cursor
            conn.close()  # Close the connection

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

    def get_trade_coins(self, indicator, symbol):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trade_coins WHERE indicator=%s AND symbol=%s", (indicator, symbol))
        row = cursor.fetchall()
        cursor.close()
        conn.close()

        return row[0]

if __name__ == '__main__':
    my_db = DataBase()
    data = my_db.get_trade_coins(indicator='SMA21')
    print(data)
