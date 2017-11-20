import os
import sys
import requests
import time
from flask import Flask, redirect, render_template, request, session, abort, url_for

app = Flask('flaskapp')

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/selector', methods=['GET', 'POST'])
def selector():
    if request.method == 'GET':
        return render_template('selector.html')
    if request.method == 'POST':
        option = request.form.getlist('options')
        test = ''
        for o in option:
            test = test + o
        return test
        # return render_template('selector.html')


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
    # HOST = '10.7.68.124'
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host=HOST, port=PORT)
