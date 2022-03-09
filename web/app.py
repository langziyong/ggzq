from flask import Flask, request, render_template, jsonify, url_for, send_file, session, redirect
import sys

sys.path.append(r"C:\Users\Administrator\Desktop\ggzq")
import api.database_io as db_io

app = Flask(__name__, static_url_path = '')
app.secret_key = "adfasdascasd"


@app.route("/")
def index():
    if "user" in session:
        return send_file("./static/html/index.html")
    else:
        return redirect(url_for("login"))


@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        if "user" in session:
            return redirect(url_for("index"))
        else:
            return send_file("./static/html/login.html")
    elif request.method == "POST":
        user = request.form.get("user", "")
        passwd = request.form.get("passwd", "")
        if user == "admin" and passwd == "123456":
            session["user"] = user
            return jsonify({
                "status": "success",
                "error": "验证成功"
            })
        else:
            return jsonify({
                "status": "fail",
                "error": "拒绝登录"
            })


@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user")
    return redirect(url_for("index"))


@app.route("/api/<operate>")
def api(operate):
    db = db_io.DatabaseIO()
    args = request.args
    if operate == "get_all_data":
        return jsonify(db.get_data(args["page"], args["limit"]))
    if operate == "get_all_source":
        return jsonify(db.get_source(args["page"], args["limit"]))
    if operate == "get_all_data_by_weights":
        return jsonify(db.get_data_by_weights(args["page"], args["limit"], args["weights"]))


if __name__ == "__main__":
    app.run(port = 80, host = "0.0.0.0", debug = True)
