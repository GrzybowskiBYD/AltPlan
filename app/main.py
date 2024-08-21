import secrets
import os


from flask import Flask, render_template, redirect, make_response, send_from_directory, request
from backend import Backend, get_themes

from URLNormalize import UrlObj


app = Flask(__name__, template_folder="./static/HTML")
app.secret_key = secrets.token_hex()

zs = Backend()


app.config['UPLOAD_FOLDER'] = "conf/backgrounds"


def send_response(prefix, timetable_id, file, repl=False):
    temp = zs.nav_list
    # Todo apply UrlObj from URLNormalize
    url = f"plany/{prefix}{timetable_id}.html"
    plan = zs.get_class_timetable(url)
    if repl:
        try:
            if prefix == "o":
                replacements = zs.get_class_subs(url)
            elif prefix == "n":
                replacements = zs.get_teacher_subs(UrlObj(f"{prefix}{timetable_id}"))
            else:
                replacements = ""
        except ValueError:
            replacements = ""
    else:
        replacements = ""
    return make_response(render_template(template_name_or_list=file,
                                         parse_classes=temp["classes"].items(),
                                         parse_teachers=temp["teachers"].items(),
                                         parse_classrooms=temp["classrooms"].items(),
                                         plan=plan,
                                         current_class=zs.url_to_name(url),
                                         replacements=replacements,
                                         # Todo apply UrlObj from URLNormalize
                                         url=f"{prefix}{timetable_id}",
                                         weekday=zs.weekday,
                                         lucky_numbers=zs.get_lucky_number(),
                                         info=zs.info,
                                         motd=len(zs.get_html_subs()[0]) > 1,
                                         hide_mobile_groups=prefix == "o",
                                         change_date=zs.change_date))


@app.route("/")
@app.route("/<string:class_url>")
def desktop(class_url=None, file="main.html"):
    if class_url:
        return send_response(class_url[0], class_url[1:], file, repl=class_url[0] in ("o", "n"))
    return redirect("/o1")


@app.route("/m")
@app.route("/m/")
@app.route("/m/<string:class_url>")
def mobile(class_url=None, file="mobile.html"):
    if class_url:
        return send_response(class_url[0], class_url[1:], file, repl=class_url[0] == "o")
    return redirect("/m/o1")


@app.route("/basic")
@app.route("/basic/")
@app.route("/basic/<string:class_url>")
def basic(class_url=None, file="basic.html"):
    if class_url:
        return send_response(class_url[0], class_url[1:], file, repl=class_url[0] == "o")
    return redirect("/basic/o1")


@app.route("/m/refresh", methods=["GET", "POST"])
@app.route("/refresh", methods=["GET", "POST"])
def refresh():
    suffix = request.args["plan"]
    zs.refresh()
    return redirect(f"/m/{suffix}" if "/m" in request.path else f"/{suffix}")


@app.route("/check_hash")
def check_hash():
    zs.heartbeat()
    return redirect("/", 301)


@app.route("/ustawienia", methods=["GET", "POST"])
def settings(file="settings.html"):
    suffix = [x for x in request.args.keys()][0] if len(request.args) > 0 else None
    if os.path.exists("conf/backgrounds"):
        backgrounds = [file for file in [f for f in os.listdir("conf/backgrounds") if os.path.isfile(os.path.join("conf/backgrounds", f))]]
    else:
        backgrounds = []
    response = make_response(render_template(template_name_or_list=file,
                                             suffix=suffix,
                                             color_schemes=get_themes(),
                                             backgrounds=backgrounds))
    return response


@app.route("/wychowawcy")
def teachers_table(file="basic.html"):
    plan = zs.teachers_table()
    response = make_response(render_template(template_name_or_list=file,
                                             plan=plan,
                                             current_class="",
                                             weekday=zs.weekday,
                                             date=zs.date.strftime("%d.%m.%Y"),
                                             lucky_numbers=zs.get_lucky_number(),
                                             info=zs.info,
                                             motd=len(zs.get_html_subs()[0]) > 1))
    return response


@app.route("/zastepstwa")
def repls(file="substitutions.html"):
    temp = zs.nav_list
    html_repl = zs.get_html_subs()
    response = make_response(render_template(template_name_or_list=file,
                                             parse_classes=temp["classes"].items(),
                                             parse_teachers=temp["teachers"].items(),
                                             parse_classrooms=temp["classrooms"].items(),
                                             replacements=(html_repl[0], html_repl[1].items())))
    return response


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static/media"), "favicon.ico",
                               mimetype="image/vnd.microsoft.icon")


@app.route("/lucky_numbers.txt")
def ln():
    return send_from_directory(os.path.join(app.root_path), "conf/lucky_numbers.txt", mimetype="text/plain")


@app.route('/backgrounds/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
