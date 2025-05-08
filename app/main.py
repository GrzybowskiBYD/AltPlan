import secrets
import os
import locale

from flask import Flask, render_template, redirect, make_response, send_from_directory, request, abort

from backend import Backend, get_themes
from URLNormalize import UrlObj
from __version__ import __version__


app = Flask(__name__, template_folder="./static/HTML")
app.secret_key = secrets.token_hex()
app.jinja_env.add_extension("jinja2.ext.loopcontrols")

zs = Backend()


app.config['UPLOAD_FOLDER'] = "conf/backgrounds"


def send_response(prefix, timetable_id, file, repl=False):
    temp = zs.nav_list

    url = f"{prefix}{timetable_id}"
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
    if os.path.exists("conf/backgrounds"):
        backgrounds = [file for file in [f for f in os.listdir("conf/backgrounds") if
                                         os.path.isfile(os.path.join("conf/backgrounds", f))]]
    else:
        backgrounds = []
    html_repl = zs.get_html_subs()
    return make_response(render_template(template_name_or_list=file,
                                         parse_classes=temp["classes"].items(),
                                         parse_teachers=temp["teachers"].items(),
                                         parse_classrooms=temp["classrooms"].items(),
                                         plan=plan,
                                         current_class=zs.url_to_name(url),
                                         replacements=replacements,
                                         url=UrlObj(f"{prefix}{timetable_id}"),
                                         weekday=zs.weekday,
                                         lucky_numbers=zs.get_lucky_number(),
                                         info=zs.info,
                                         motd=len(zs.get_html_subs()[0]) > 1,
                                         motd_info=(html_repl[0], html_repl[1].items()),
                                         hide_mobile_groups=prefix == "o",
                                         change_date=zs.change_date,
                                         color_schemes=get_themes(),
                                         backgrounds=backgrounds,
                                         date=zs.date,
                                         app_version=__version__))


@app.route("/")
@app.route("/<string:class_url>")
def desktop(class_url=None, file="main.html"):
    if class_url:
        prefix = class_url[0]
        object_id = class_url[1:]
        if class_url in zs.nav_list_keys:
            return send_response(prefix, object_id, file, repl=prefix in ("o", "n"))
        else:
            abort(404)
    return redirect("/o1")


@app.route("/m")
@app.route("/m/")
@app.route("/m/<string:class_url>")
def mobile(class_url=None, file="mobile.html"):
    if class_url:
        if class_url in zs.nav_list:
            prefix = class_url[0]
            object_id = class_url[1:]
            return send_response(prefix, object_id, file, repl=prefix in ("o", "n"))
        else:
            abort(404)
    return redirect("/m/o1")


@app.route("/basic")
@app.route("/basic/")
@app.route("/basic/<string:class_url>")
def basic(class_url=None, file="basic.html"):
    if class_url:
        prefix = class_url[0]
        object_id = class_url[1:]
        return send_response(prefix, object_id, file, repl=object_id == "o")
    return redirect("/basic/o1")


@app.route("/m/refresh", methods=["GET", "POST"])
@app.route("/refresh", methods=["GET", "POST"])
def refresh():
    zs.refresh()

    if "r" in request.args.keys():
        redirect_destination = request.args["r"]
    else:
        redirect_destination = "o1"

    if "/m" in request.path:
        return redirect(f"/m/{redirect_destination}")
    return redirect(f"/{redirect_destination}")


@app.route("/check_hash")
def check_hash_for_change():
    zs.heartbeat()
    return redirect("/", 301)


@app.route("/ustawienia", methods=["GET", "POST"])
def settings(file="settings.html"):
    if "r" in request.args.keys():
        redirect_destination = request.args["r"]
    else:
        return redirect("/ustawienia?r=o1", 301)

    if os.path.exists("conf/backgrounds"):
        backgrounds = [file for file in [f for f in os.listdir("conf/backgrounds") if os.path.isfile(os.path.join("conf/backgrounds", f))]]
        app.logger.error("ta" + str(backgrounds))
    else:
        app.logger.error("nie")
        backgrounds = []

    response = make_response(render_template(template_name_or_list=file,
                                             redirect_destination=redirect_destination,
                                             color_schemes=get_themes(),
                                             backgrounds=backgrounds,
                                             app_version=__version__))
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
    return send_response("o", "1", file)


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


@app.route('/error/<int:code>')
def error(code):
    abort(int(code))


# ERROR HANDLERS #
@app.errorhandler(Exception)
def page_not_found(e):
    return make_response(render_template(template_name_or_list="error.html", error_data=e), e.code)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
