
from flask import Flask, render_template, request
from app import

web = Flask(__name__)

@web.route('/')
def hello_world():
    return render_template('index.html')

if __name__ == '__main__':
    web.run(debug=True)
