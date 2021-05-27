from flask import Flask
app=Flask(__name__)

#Use Flask to create my routes
@app.route("/")
def home():
    print("api instructions")