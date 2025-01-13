
from flask import Flask, render_template, request
from app import check_signals_with_ema

web = Flask(__name__)

@web.route('/')
def get_bot_data():
    crossover_result = check_signals_with_ema()
    return render_template('index.html')

if __name__ == '__main__':
    web.run(debug=True)
