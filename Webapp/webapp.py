import os
import sys
import requests
import time
from multiprocessing import Process
from flask import Flask, redirect, render_template, request, session, abort, url_for

from sound_processing import process_signal
from demo_code import demo_movement
from computer_vision import clean_motion

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
            audio_p, video_p, demo_p = start_process(process_signal.detect_sound, audio_p, video_p, demo_p)
        if selected == 'camera':
            video_p, audio_p, demo_p = start_process(clean_motion.detect_motion, video_p, audio_p, demo_p)
        if selected == 'demo':
            demo_p, audio_p, video_p = start_process(demo_movement.loop_msg, demo_p, audio_p, video_p)
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

def start_process(target_method, p_to_start, p1_to_stop, p2_to_stop):
    if p_to_start != None and p_to_start.is_alive():
        pass
    else:
        p1_to_stop = stop_process(p1_to_stop)
        p2_to_stop = stop_process(p2_to_stop)
        p_to_start = Process(target=target_method, args=(True,))
        p_to_start.start()
    return p_to_start, p1_to_stop, p2_to_stop


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
    # HOST = '10.7.68.124'
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host=HOST, port=PORT)
