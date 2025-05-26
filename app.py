from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import pyotp
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
import base64, os
from datetime import timedelta
import qrcode
import io

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=5)

key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

users = {"testuser": {"password": "password123", "totp_secret": pyotp.random_base32(), "verified": True}}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/create_account', methods=['POST'])
def create_account():
    username = request.form.get('username')
    encrypted_password = request.form.get('password')
    
    if username in users:
        return "Username exists", 400
    
    try:
        cipher = PKCS1_OAEP.new(RSA.import_key(private_key), hashAlgo=SHA256)
        password = cipher.decrypt(base64.b64decode(encrypted_password)).decode('utf-8')
        users[username] = {
            "password": password,
            "totp_secret": pyotp.random_base32(),
            "verified": False
        }
        session['username'] = username
        return redirect(url_for('setup_totp'))
    except:
        return "Registration failed", 500

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    if username not in users:
        return "Invalid username", 401
    
    try:
        cipher = PKCS1_OAEP.new(RSA.import_key(private_key), hashAlgo=SHA256)
        password = cipher.decrypt(base64.b64decode(request.form['password'])).decode('utf-8')
        
        if password == users[username]['password']:
            if not users[username]['verified']:
                return "Complete TOTP setup", 401
            session['username'] = username
            return redirect(url_for('totp_page'))
        return "Invalid password", 401
    except:
        return "Login failed", 500

@app.route('/get_public_key')
def get_public_key():
    return jsonify({'public_key': public_key.decode()})

@app.route('/setup_totp')
def setup_totp():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session['username']
    totp_secret = users[username]['totp_secret']
    # Generate provisioning URI
    uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(name=username, issuer_name="AuthVault")
    # Generate QR code image
    qr = qrcode.make(uri)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    qr_data_url = f"data:image/png;base64,{qr_b64}"
    return render_template('setup_totp.html', totp_secret=totp_secret, qr_code=qr_data_url)

@app.route('/verify_setup', methods=['POST'])
def verify_setup():
    if 'username' not in session:
        return redirect(url_for('index'))
    if pyotp.TOTP(users[session['username']]['totp_secret']).verify(request.form['totp_code']):
        users[session['username']]['verified'] = True
        return redirect(url_for('success'))
    return "Invalid code", 401

@app.route('/success')
def success():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session['username']
    return render_template('success.html', username=username)

@app.route('/totp_page')
def totp_page():
    return render_template('totp.html') if 'username' in session else redirect(url_for('index'))

@app.route('/verify_totp', methods=['POST'])
def verify_totp():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session['username']
    totp_code = request.form['totp_code']
    if pyotp.TOTP(users[username]['totp_secret']).verify(totp_code):
        return redirect(url_for('success'))
    return "Invalid TOTP code", 401

if __name__ == '__main__':
    app.run(debug=True)