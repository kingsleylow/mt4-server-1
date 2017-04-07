#!/usr/local/bin/python3
# -*- coding: UTF-8 -*-

import os
from flask import Flask, session, redirect, url_for, escape, request, send_from_directory
from werkzeug import secure_filename
import hashlib
import json
import pymysql

app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = 'tmp/'

db = pymysql.connect(
    host = "localhost",
    port = 3306,
    user = "root",
    passwd = "123456",
    db = "rss",
    charset = 'utf8'
    )   
    #cursorclass = pymysql.cursors.SSCursor) ### No longer needed in pymysql

db.autocommit(1)
cursor = db.cursor()

### SHA256
KEY = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"

@app.route('/', methods=['GET'])
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    else:
        return 'You have no permission.'
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        ### Password is admin
        if hashlib.sha256((request.form['password']).encode('utf-8')).hexdigest() != KEY:
            return '''
                <p>ERROR: Wrong Password!</p>
            '''
        return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    if 'username' not in session:
        return 'You must login.'
    ### remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/api/v1/alive', methods=['GET'])
def alive():
    if request.headers.get("Key") != KEY:
        return "No key found."
    if request.method == 'POST':
        data = "What you post is %s" % request.get_data()
        return data
    return "Service OK."

@app.route('/api/v1/post_trade', methods=['GET', 'POST'])
def post_trade():
    if request.headers.get("Key") != KEY:
        return "No key found."
    if request.method == 'POST':
        data = "What you post is %s" % request.get_data()
        return data
    return "This is trade-posting page."

@app.route('/api/v1/get_all')
def get_all():
    if request.json.get('username'):
        print(request.json.get('username'))
    if 'username' not in session:
        return 'You must login.'
    return 'All messages!'

@app.route('/get/<int:post_id>')
def get(post_id):
    if 'username' not in session:
        return 'You must login.'
    return 'ID: %s' % post_id

def allowed_file(filename):
    if 'username' not in session:
        return 'You must login.'
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'username' not in session:
        return 'You have no permission.'
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if 'username' not in session:
        return 'You have no permission.'
    #return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return "File %s uploaded!" % filename

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(host='0.0.0.0', port=5000, debug = True)
