from flask import Flask

app = Flask(__name__)

@app.route("/order")
def order_page():
    return "<!doctype html><html><body><h1>ORDER TEST OK</h1></body></html>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
