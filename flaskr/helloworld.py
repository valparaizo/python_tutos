from flask import Flask
app = Flask(__name__)

@app.route("/hello")
def hello():
    return "Hello World!"

# permet à wing de fonctionner en debug
if __name__ == '__main__':
    app.debug = False
    app.run()