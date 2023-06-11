from flask import Flask, request, send_file
from cryptography.fernet import Fernet
import os

import time

import json
f = open('config.json')
config = json.load(f)

print('KEY: ', config['key'])

app = Flask(__name__)
key = config['key']
upload_folder = "uploaded_files/"
encrypted_folder = "encrypted_files/"
decrypted_folder = "decrypted_files/"

def generate_key():
    return Fernet.generate_key()

def save_file(file, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = file.filename
    filepath = os.path.join(folder, filename)
    file.save(filepath)
    return filename

def encrypt_file(filename):
    if not os.path.exists(encrypted_folder):
        os.makedirs(encrypted_folder)
    f = Fernet(key)
    with open(os.path.join(upload_folder, filename), 'rb') as file:
        data = file.read()
        encrypted_data = f.encrypt(data)
        time_stamp = str(time.time())
        encrypted_filename = time_stamp + filename + '.enc'
        with open(os.path.join(encrypted_folder, encrypted_filename), 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)
        return encrypted_filename

def decrypt_file(filename):
    if not os.path.exists(decrypted_folder):
        os.makedirs(decrypted_folder)
    f = Fernet(key)
    with open(os.path.join(encrypted_folder, filename), 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
        decrypted_data = f.decrypt(encrypted_data)
        decrypted_filename = filename[:-4]
        with open(os.path.join(decrypted_folder, decrypted_filename), 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)
        return decrypted_filename

@app.route('/upload', methods=['POST'])
def upload():
    print(request.files)
    uploaded_file = request.files['file']
    filename = save_file(uploaded_file, upload_folder)
    encrypted_filename = encrypt_file(filename)
    return f'File "{filename}" uploaded and encrypted as "{encrypted_filename}".'
    return "test"

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    decrypted_filename = decrypt_file(filename)
    return send_file(os.path.join(decrypted_folder, decrypted_filename))

if __name__ == '__main__':
    key = generate_key()
    app.run()
