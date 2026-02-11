from flask import Flask, request, send_from_directory, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = './storage'
LATEST_FILE = {"filename": None} # This acts as a simple status flag

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    LATEST_FILE['filename'] = file.filename # Update the flag
    return "Uploaded", 200

@app.route('/check-for-files', methods=['GET'])
def check():
    return jsonify(LATEST_FILE)

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)