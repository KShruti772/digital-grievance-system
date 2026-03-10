from flask import Blueprint, render_template, redirect, url_for, session

app = Blueprint('app', __name__)

@app.route('/')
def index():
    # if a user is authenticated, redirect based on their role
    role = session.get('role')
    if role == 'citizen':
        return redirect(url_for('citizen.dashboard'))
    elif role == 'officer':
        return redirect(url_for('officer.dashboard'))
    elif role == 'worker':
        return redirect(url_for('worker.dashboard'))
    # otherwise show public homepage
    return render_template('index.html')
