import ccxt

# Initialize exchanges
binance = ccxt.binance()
kucoin = ccxt.kucoin()

# Load available markets from both exchanges
binance_markets = binance.load_markets()
kucoin_markets = kucoin.load_markets()

# Define your investment and trading fee (e.g., 0.1% or 0.001)
investment_usd = 10000.0
trading_fee = 0.001  # 0.1% fee per trade


# Function to get price from an exchange
def get_price(exchange, pair):
    try:
        ticker = exchange.fetch_ticker(pair)
        return ticker['bid'], ticker['ask']  # bid: buy price, ask: sell price
    except Exception as e:
        print(f"Error fetching data for {pair}: {e}")
        return None, None


# Function to calculate potential profit after fees
def calculate_profit(investment, buy_price, sell_price, fee):
    # Deduct the fee for buying (investment decreases slightly due to fees)
    effective_investment = investment * (1 - fee)
    # Calculate how much crypto you can buy after paying fees
    amount_crypto = effective_investment / buy_price
    # Calculate sell value and deduct the fee for selling
    sell_value = amount_crypto * sell_price * (1 - fee)
    # Calculate the net profit
    profit = sell_value - investment
    profit_percent = (profit / investment) * 100
    return profit, profit_percent


# Function to find arbitrage opportunity with net profit calculation
def find_arbitrage(pair):
    binance_bid, binance_ask = get_price(binance, pair)
    kucoin_bid, kucoin_ask = get_price(kucoin, pair)

    if binance_bid is None or kucoin_bid is None:
        return

    # Binance -> Kucoin Arbitrage (Buy on Binance, Sell on Kucoin)
    if binance_ask < kucoin_bid:
        profit, profit_percent = calculate_profit(investment_usd, binance_ask, kucoin_bid, trading_fee)
        print(f"Arbitrage opportunity for {pair} - Buy on Binance ({binance_ask}) -> Sell on Kucoin ({kucoin_bid}) | "
              f"Net Profit: {profit:.2f} USDT ({profit_percent:.2f}%) with investment of {investment_usd} USDT")

    # Kucoin -> Binance Arbitrage (Buy on Kucoin, Sell on Binance)
    if kucoin_ask < binance_bid:
        profit, profit_percent = calculate_profit(investment_usd, kucoin_ask, binance_bid, trading_fee)
        print(f"Arbitrage opportunity for {pair} - Buy on Kucoin ({kucoin_ask}) -> Sell on Binance ({binance_bid}) | "
              f"Net Profit: {profit:.2f} USDT ({profit_percent:.2f}%) with investment of {investment_usd} USDT")


# Find common trading pairs between Binance and KuCoin
common_pairs = set(binance_markets.keys()).intersection(kucoin_markets.keys())

# Loop through common pairs and find arbitrage opportunities
for pair in common_pairs:
    find_arbitrage(pair)
