from flask import Flask
app = Flask(__name__)  # <-- Add the missing underscore
@app.route('/')
def hello():
    return "Hello, World!"
