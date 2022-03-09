from flask import Flask, request, render_template, jsonify, url_for, send_file
import sys


sys.path.append(r"C:\Users\Administrator\Desktop\ggzq")
import api.database_io as db_io

app = Flask(__name__, static_url_path = '')


@app.route("/")
def index():
    return send_file("./static/html/index.html")


@app.route("/api/<operate>")
def api(operate):
    db = db_io.DatabaseIO()
    _args = request.args
    _operate = operate
    if operate == "get_all_data":
        return jsonify(db.get_data(_args["page"], _args["limit"]))
    if operate == "get_all_source":
        return jsonify(db.get_source(_args["page"], _args["limit"]))


if __name__ == "__main__":
    app.run(port = 80, host = "0.0.0.0")
