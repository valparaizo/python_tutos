from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello BluePrism !"

@app.route('/order/<num>')
def order(num):
	return "{ \"Order Number\": \"ORDER-" + num + "C\"}"

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)