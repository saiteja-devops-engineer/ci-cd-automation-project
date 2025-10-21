from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hey! This app is created usinf Python's Flask Framework."

if __name__=='__main__':
    app.run()