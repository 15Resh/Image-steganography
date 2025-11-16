from flask import Flask, render_template, request, send_from_directory
import os
from werkzeug.utils import secure_filename
from PIL import Image
import hashlib  # For password hashing
from stegano import lsb  # Use stegano for LSB steganography

app = Flask(__name__)
UPLOAD_FOLDER = "static"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def hash_password(password):
    """Hash the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/")
def index():
    return render_template("template.html")

@app.route("/encode", methods=["POST"])
def encode_message():
    """Encode message into an image using LSB steganography"""
    if "image" not in request.files or "message" not in request.form or "password" not in request.form:
        return "Missing required fields", 400

    image = request.files["image"]
    message = request.form["message"]
    password = request.form["password"]

    if image.filename == "":
        return "No selected file", 400

    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(image_path)

    # Hash the password and append it to the message
    hashed_password = hash_password(password)
    secure_message = f"{hashed_password}:{message}"

    # Encode message into image
    encoded_img = lsb.hide(image_path, secure_message)
    encoded_path = os.path.join(app.config["UPLOAD_FOLDER"], "encoded_" + filename)
    encoded_img.save(encoded_path)

    return f"Image encoded successfully! <a href='/static/encoded_{filename}' download>Download</a>"

@app.route("/decode", methods=["POST"])
def decode_message():
    """Decode hidden message from an image"""
    if "image" not in request.files or "password" not in request.form:
        return "Missing required fields", 400

    image = request.files["image"]
    password = request.form["password"]

    if image.filename == "":
        return "No selected file", 400

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(image.filename))
    image.save(image_path)

    # Decode message from image
    try:
        hidden_data = lsb.reveal(image_path)
    except Exception as e:
        return f"Error decoding message: {e}", 400

    # Extract stored password and message
    try:
        stored_hash, hidden_message = hidden_data.split(":", 1)
    except ValueError:
        return "Error decoding message", 400

    # Check password
    if hash_password(password) != stored_hash:
        return "Incorrect password", 403

    return f"Decoded Message: {hidden_message}"

if __name__ == "__main__":
    app.run(debug=True)
