import os
import sys
import requests
import time
from multiprocessing import Process
from flask import Flask, redirect, render_template, request, session, abort, url_for

from sound_processing import process_signal

app = Flask('flaskapp')
global audio_p
audio_p = None
global video_p
video_p = None
global demo_p
demo_p = None

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/selector', methods=['GET', 'POST'])
def selector():
    if request.method == 'GET':
        return render_template('selector.html', i_select = 'off')
    if request.method == 'POST':
        inputs = request.form.getlist('inputs')
        for i in inputs:
            print(i)
        global audio_p
        global video_p
        global demo_p
        selected = inputs[0]
        if selected == 'audio':
            if audio_p != None and audio_p.is_alive():
                pass
            else:
                video_p = stop_process(video_p)
                demo_p = stop_process(demo_p)
                audio_p = Process(target=process_signal.detect_sound)
                audio_p.start()
        if selected == 'off':
            video_p = stop_process(video_p)
            demo_p = stop_process(demo_p)
            audio_p = stop_process(audio_p)
        return render_template('selector.html', i_select = inputs[0])

def stop_process(my_process):
    if my_process != None and my_process.is_alive():
        my_process.terminate()
        return None
    return my_process


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
    # HOST = '10.7.68.124'
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host=HOST, port=PORT)
