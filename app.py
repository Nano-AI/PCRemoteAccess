from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from multiprocessing import Process
import json
import ctypes
import subprocess

app = Flask(__name__)

with open('config.json') as f:
    config = json.load(f)

# app.secret_key = 'adsdfdfdfdf'
app.secret_key = ':\xd4\x9cc|\x95\xd0 \xcf\x1f\nvK\x16\x9b\x05\xfePo\xc8\x81\xec\x10?'


@app.route("/")
def index():
    return redirect(url_for('login'))


@app.route("/home", methods=["POST", "GET"])
def home():
    if session.get('username') != config['username'] or session.get('password') != config['password']:
        return redirect(url_for('login'))
    return render_template('home.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if check_right_credentials(session.get('username'), session.get('password')):
        return redirect(url_for('home'))
    error = None
    if session.get('username') != config['username'] or session.get('password') != config['password']:
        if request.method == 'POST':
            print(request.form['username'], request.form['password'])
            if request.form['username'] != config['username'] or request.form['password'] != config['password']:
                error = 'Invalid Credentials. Please try again.'
            else:
                session['username'] = request.form['username']
                session['password'] = request.form['password']
                return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route("/popup", methods=["POST"])
def popup():
    if session.get('username') != config['username'] or session.get('password') != config['password']:
        return ''
    popup_process = Process(
        target=make_popup,
        daemon=True,
        args=(0, request.form.get("text"), request.form.get("title"), int(request.form.get("style")))
    )
    popup_process.start()
    return ''


@app.route("/lock", methods=["POST"])
def lock():
    if session.get('username') != config['username'] or session.get('password') != config['password']:
        return redirect(url_for('login'))
    ctypes.windll.user32.LockWorkStation()
    return redirect(url_for('home'))


@app.route("/execute/<command>", methods=["GET"])
def execute(command):
    if session.get('username') != config['username'] or session.get('password') != config['password']:
        return redirect(url_for('login'))
    if command is None:
        return jsonify({'error': 'No command given.'})
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = result.stdout, result.stderr
    if out is not None:
        out = out.read()
    if error is not None:
        error = error.read()
    return jsonify({'output': out.decode("utf-8"), 'error': error.decode("utf-8")})


def check_right_credentials(username: str, password: str) -> bool:
    return username == config['username'] and password == config['password']


def make_popup(button_style: int, text: str, title: str, icon: int):
    ctypes.windll.user32.MessageBoxW(button_style, text, title, icon, 0x40000)


if __name__ == "__main__":
    app.run(debug=True)
