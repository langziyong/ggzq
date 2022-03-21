import json
from flask import Flask, request, render_template, jsonify, url_for, send_file, session, redirect
import sys

sys.path.append(r"../")
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
        db = db_io.DatabaseIO()
        USER = json.loads(db.config("USER")["USER"])
        if user in USER and passwd == USER[user]:
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


# 关键词查询
def keyword_query_(compared_data, keyword_list, weights_limit):
    result = []
    discard = 0
    for target in compared_data:
        target["weights"] = 0
        for keyword in keyword_list:
            if keyword in target["target_title"]: target["weights"] += 1
        if target["weights"] >= weights_limit:
            result.append(target)
        else:
            discard += 1

    return [discard, result]


@app.route("/api/<operate>", methods = ["GET", "POST"])
def api(operate):
    if "user" in session:
        pass
    else:
        return redirect(url_for("login"))
    db = db_io.DatabaseIO()
    args = request.args
    if operate == "get_all_data":
        return jsonify(db.get_data(args["page"], args["limit"]))
    if operate == "get_source":
        return jsonify(db.get_source(args["page"], args["limit"]))
    if operate == "get_all_data_by_weights":
        return jsonify(db.get_data_by_weights(args["page"], args["limit"], args["weights"]))
    if operate == "get_config":
        if request.method == "POST":
            new_data = request.form
            return db.config(new_data = {
                "SYSTEM_CONFIG": {
                    "THREAD_N": new_data["thread_n"],
                    "PROCESS_N": new_data["process_n"],
                    "ASYNC_TASK_N": new_data["async_task_n"],
                    "TITLE_LENGTH": new_data["title_length"],
                    "GET_HTML_TIMEOUT": new_data["get_html_timeout"],
                    "TITLE_SEARCH_DEPTH": new_data["title_search_depth"],
                    "EFFECTIVE_TIME_DIFFERENCE": new_data["effective_time_difference"],
                    "WEIGHTS_LIMIT": new_data["weights_limit"]
                },
                "KEYWORD": [i for i in new_data["keyword"].split(",")]
            })
        else:
            return jsonify(db.config())
    if operate == "data_self_check":
        count = {
            "repeat_discard": 0,
            "weights_discard": 0,
            "origin_total": 0,
            "new_total": 0
        }
        result = []
        config = db.config()
        weights = int(json.loads(config["SYSTEM_CONFIG"])["WEIGHTS_LIMIT"])
        keyword = json.loads(config["KEYWORD"])
        all_target_url = db.get_all_target_url()
        all_data = db.get_data(1, 100000)["data"]
        count["origin_total"] = len(all_data)

        target_title_ = []
        while len(all_data) != 0:
            i = all_data.pop()
            if i["target_title"] not in target_title_:
                result.append(i)
                target_title_.append(i["target_title"])

        result = keyword_query_(result, keyword, weights)
        db.clearn_result()
        db.upload_result(result[1])
        count["weights_discard"] = result[0]
        count["new_total"] = len(result[1])
        return jsonify(count)


@app.route("/manageApi/<operate>", methods = ["GET", "POST"])
def manage_api(operate):
    if "user" in session:
        pass
    else:
        return redirect(url_for("login"))
    db = db_io.DatabaseIO()
    args = request.args
    if operate == "edit":
        data = db.get_source_detailed(args["id"])
        return render_template("edit_page.html", data = data)
    if operate == "update_source":
        return jsonify(db.source_update(request.form.to_dict()))
    if operate == "disabled":
        return jsonify(db.source_update({"id": args.get("id"), "disabled": args.get("v")}))
    if operate == "delete":
        return jsonify(db.delete(args.get("id")))
    if operate == "add_source":
        return render_template("edit_page.html",data = {})


if __name__ == "__main__":
    app.run(port = 80, host = "0.0.0.0")
