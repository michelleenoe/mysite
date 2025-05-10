import os
import git

from flask import Flask, session, render_template, request, redirect, url_for, jsonify, flash, abort
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import time
import uuid
from random import randint
from datetime import datetime, timedelta
import x
from icecream import ic
from functools import wraps
from translations import da, en

ic.configureOutput(prefix='----- | ', includeContext=True)

# ----------------------------------------
# “Hemmelig” webhook-URL (hardcoded til test)
# ----------------------------------------
GIT_HOOK_SECRET = "secret_url_for_git_hook"

# ----------------------------------------
# Flask-app
# ----------------------------------------
app = Flask(__name__)
app.secret_key = "hemmelig"                # Hemmelig nøgle hardcoded
app.config['SESSION_TYPE']       = 'filesystem'
app.config['UPLOAD_FOLDER']      = 'static/uploads'
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024 * 5
Session(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ----------------------------------------
# GitHub Webhook: automatisk pull fra main
# ----------------------------------------
@app.route(f"/{GIT_HOOK_SECRET}", methods=["POST"])
def git_update():
    """
    Modtag POST fra GitHub og pull main-branchen.
    """
    repo_path = os.path.dirname(os.path.abspath(__file__))
    repo = git.Repo(repo_path)
    origin = repo.remotes.origin

    origin.fetch()
    repo.heads.main.set_tracking_branch(origin.refs.main)
    repo.heads.main.checkout()
    origin.pull()

    return "", 204


# ----------------------------------------
# Hjælpe- og valideringsfunktioner
# ----------------------------------------
def get_text(key):
    lang = session.get("lang", "da")
    return (en.translations if lang == "en" else da.translations).get(key, key)


@app.context_processor
def inject_globals():
    return {
        "get_text": get_text,
        "session": session,
        "x": x,
        "old_values": {}
    }


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = session.get("user")
        if not user or user.get("user_role") != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            lang = kwargs.get("lang") or request.view_args.get("lang") or session.get("lang", "da")
            return redirect(url_for("show_login", lang=lang))
        return f(*args, **kwargs)
    return decorated


@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"]        = "no-cache"
    response.headers["Expires"]       = "0"
    return response


@app.before_request
def set_language_from_url():
    lang = request.view_args.get("lang") if request.view_args else None
    if lang in ("da", "en"):
        session["lang"] = lang
    elif "lang" not in session:
        session["lang"] = "da"


# ----------------------------------------
# Routes
# ----------------------------------------
@app.get("/")
def redirect_to_language():
    lang = session.get("lang", "da")
    return redirect(url_for("page_index", lang=lang))


@app.get("/<lang>/")
def page_index(lang):
    try:
        db, cursor = x.db()
        cursor.execute("SELECT * FROM items WHERE item_status = 'aktiv'")
        items = cursor.fetchall()
        return render_template("page_index.html", title=get_text("title"), items=items)
    except Exception as ex:
        ic(ex)
        return "System under maintenance", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


@app.get("/<lang>/login")
def show_login(lang):
    if session.get("user"):
        return redirect(url_for("profile", lang=lang))
    return render_template("page_login.html", title=get_text("login"), lang=lang)


@app.post("/<lang>/login")
def login(lang):
    try:
        user_email    = x.validate_user_email()
        user_password = x.validate_user_password()
        db, cursor    = x.db()
        cursor.execute("SELECT * FROM users WHERE user_email = %s", (user_email,))
        user = cursor.fetchone()
        if not user or not check_password_hash(user["user_password"], user_password) or not user["user_is_verified"]:
            raise Exception(get_text("invalid_login"))
        session["user"] = dict(user)
        return redirect(url_for("profile", lang=lang))
    except Exception as ex:
        ic(ex)
        return render_template("page_login.html", title=get_text("login"), error_message=str(ex))
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


@app.get("/<lang>/logout")
def logout(lang):
    session.clear()
    return redirect(url_for("page_index", lang=lang))


@app.get("/<lang>/profile")
@login_required
def profile(lang):
    user = session["user"]
    if user["user_role"] == "admin":
        return redirect(url_for("admin_dashboard", lang=lang))

    try:
        db, cursor = x.db()
        cursor.execute("""
            SELECT i.*,
                   (
                     SELECT image_path
                       FROM item_images
                      WHERE item_fk = i.item_pk
                      ORDER BY image_created_at
                      LIMIT 1
                   ) AS first_image
              FROM items AS i
             WHERE i.item_user_email = %s
             ORDER BY i.item_created_at DESC
        """, (user["user_email"],))
        user_items = cursor.fetchall()
    except Exception as ex:
        ic(ex)
        return redirect(url_for("show_login", lang=lang))
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

    return render_template("page_profile.html", user=user, user_items=user_items, title=get_text("profile"))


@app.get("/<lang>/admin/users")
@admin_required
def admin_list_users(lang):
    try:
        db, cursor = x.db()
        cursor.execute("SELECT user_pk, user_username, user_email, user_role, user_is_verified FROM users")
        users = cursor.fetchall()
        return render_template("admin_users.html", users=users)
    except Exception as ex:
        ic(ex)
        return "Systemfejl", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


@app.get("/<lang>/admin/items")
@admin_required
def admin_list_items(lang):
    try:
        db, cursor = x.db()
        cursor.execute("SELECT item_pk, item_name, item_user_email, item_status, item_created_at FROM items")
        items = cursor.fetchall()
        return render_template("admin_items.html", items=items, lang=session.get("lang", "da"))
    except Exception as ex:
        ic(ex)
        return "Systemfejl", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


@app.get("/<lang>/items/add")
@login_required
def add_item(lang):
    return render_template("page_add_item.html", title=get_text("add_item"))


@app.post("/<lang>/items/add")
@login_required
def save_item(lang):
    try:
        item_pk          = str(uuid.uuid4())
        item_name        = x.validate_item_name()
        item_address     = x.validate_item_address()
        item_lat         = x.validate_item_lat()
        item_lon         = x.validate_item_lon()
        item_description = x.validate_item_description()
        item_price       = x.validate_item_price()
        image_paths      = x.validate_item_images()

        user_email = session["user"]["user_email"]
        ts         = int(time.time())

        db, cursor = x.db()
        cursor.execute("""
            INSERT INTO items (
                item_pk, item_name, item_address, item_lat, item_lon,
                item_description, item_price,
                item_status, item_user_email, item_created_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,'aktiv',%s,%s)
        """, (
            item_pk, item_name, item_address, item_lat, item_lon,
            item_description, item_price,
            user_email, ts
        ))
        for p in image_paths:
            cursor.execute("""
                INSERT INTO item_images (
                    image_pk, item_fk, image_path, image_created_at
                ) VALUES (%s,%s,%s,%s)
            """, (str(uuid.uuid4()), item_pk, p, ts))

        db.commit()
        return redirect(url_for("profile", lang=lang), code=303)

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        msg = str(ex)
        flash(get_text(msg) if msg in da.translations else msg)
        return redirect(url_for("add_item", lang=lang))
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


@app.patch("/<lang>/admin/users/<pk>/unblock")
@admin_required
def unblock_user(lang, pk):
    try:
        db, cursor = x.db()
        cursor.execute("UPDATE users SET user_blocked_at = 0 WHERE user_pk = %s", (pk,))
        db.commit()
        return redirect(url_for("admin_list_users", lang=lang))
    except Exception as ex:
        ic(ex)
        return "Systemfejl", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


@app.post("/<lang>/admin/users/<pk>/delete")
@admin_required
def admin_delete_user(lang, pk):
    try:
        db, cursor = x.db()
        cursor.execute("DELETE FROM users WHERE user_pk = %s", (pk,))
        db.commit()
        return redirect(url_for("admin_list_users", lang=lang))
    except Exception as ex:
        return str(ex), 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


@app.post("/<lang>/admin/items/<pk>/delete")
@admin_required
def admin_delete_item(lang, pk):
    try:
        db, cursor = x.db()
        cursor.execute("DELETE FROM items WHERE item_pk = %s", (pk,))
        db.commit()
    finally:
        cursor.close()
        db.close()
    return redirect(url_for("admin_list_items", lang=lang))


@app.get("/<lang>/admin/dashboard")
@admin_required
def admin_dashboard(lang):
    db, cursor = x.db()
    cursor.execute("SELECT COUNT(*) AS c FROM users")
    total_users = cursor.fetchone()["c"]
    cursor.execute("SELECT COUNT(*) AS c FROM items WHERE item_status='aktiv'")
    active_items = cursor.fetchone()["c"]
    cursor.execute("SELECT COUNT(*) AS c FROM users WHERE user_is_verified=0")
    pending_verifications = cursor.fetchone()["c"]
    cursor.close()
    db.close()

    return render_template(
        "admin_dashboard.html",
        title=get_text("admin_dashboard_title"),
        total_users=total_users,
        active_items=active_items,
        pending_verifications=pending_verifications
    )


@app.get("/<lang>/account/edit")
@login_required
def edit_profile(lang):
    user = session["user"]
    return render_template("page_edit_profile.html", title=get_text("edit_profile"), user=user)


@app.get("/<lang>/items/<pk>/edit")
@login_required
def edit_item(lang, pk):
    db, cursor = x.db()
    cursor.execute("SELECT * FROM items WHERE item_pk = %s", (pk,))
    item = cursor.fetchone()
    cursor.close()
    db.close()

    if not item:
        abort(404)
    if item["item_user_email"] != session["user"]["user_email"]:
        abort(403)

    return render_template("page_edit_item.html", title=get_text("edit_item"), item=item)


@app.get("/<lang>/admin/items/<pk>/edit")
@admin_required
def admin_edit_item(lang, pk):
    db, cursor = x.db()
    cursor.execute("SELECT * FROM items WHERE item_pk = %s", (pk,))
    item = cursor.fetchone()
    cursor.close()
    db.close()

    if not item:
        abort(404)

    return render_template(
        "page_edit_item.html",
        title=get_text("edit_item"),
        item=item,
        admin_view=True
    )


@app.post("/<lang>/items/<pk>/edit")
@login_required
def save_edited_item(lang, pk):
    db, cursor = x.db()
    cursor.execute("SELECT item_user_email FROM items WHERE item_pk = %s", (pk,))
    row = cursor.fetchone()
    if not row:
        cursor.close(); db.close(); abort(404)
    if row["item_user_email"] != session["user"]["user_email"]:
        cursor.close(); db.close(); abort(403)
    try:
        item_name        = x.validate_item_name(field="name")
        item_address     = x.validate_item_address(field="address")
        item_lat         = x.validate_item_lat(field="lat")
        item_lon         = x.validate_item_lon(field="lon")
        item_description = x.validate_item_description(field="description")
        item_price       = x.validate_item_price(field="price")
        image_paths      = x.validate_item_images(optional=True)

        ts = int(time.time())
        cursor.execute("""
            UPDATE items
               SET item_name        = %s,
                   item_address     = %s,
                   item_lat         = %s,
                   item_lon         = %s,
                   item_description = %s,
                   item_price       = %s,
                   item_updated_at  = %s
             WHERE item_pk         = %s
        """, (
            item_name, item_address, item_lat, item_lon,
            item_description, item_price,
            ts, pk
        ))
        for path in image_paths:
            cursor.execute("""
                INSERT INTO item_images (
                    image_pk, item_fk, image_path, image_created_at
                ) VALUES (%s,%s,%s,%s)
            """, (str(uuid.uuid4()), pk, path, ts))

        db.commit()
        flash(get_text("save_changes_success"), "success")
        return redirect(url_for("profile", lang=lang))
    except Exception as ex:
        db.rollback()
        flash(str(ex), "error")
        return redirect(url_for("edit_item", lang=lang, pk=pk))
    finally:
        cursor.close()
        db.close()


@app.post("/<lang>/admin/items/<pk>/edit")
@admin_required
def admin_save_edited_item(lang, pk):
    try:
        item_name        = x.validate_item_name(field="name")
        item_address     = x.validate_item_address(field="address")
        item_lat         = x.validate_item_lat(field="lat")
        item_lon         = x.validate_item_lon(field="lon")
        item_description = x.validate_item_description(field="description")
        item_price       = x.validate_item_price(field="price")
        image_paths      = x.validate_item_images(field="images")

        db, cursor = x.db()
        ts = int(time.time())
        cursor.execute("""
            UPDATE items
               SET item_name        = %s,
                   item_address     = %s,
                   item_lat         = %s,
                   item_lon         = %s,
                   item_description = %s,
                   item_price       = %s,
                   item_updated_at  = %s
             WHERE item_pk         = %s
        """, (
            item_name, item_address, item_lat, item_lon,
            item_description, item_price,
            ts, pk
        ))
        for path in image_paths:
            cursor.execute("""
                INSERT INTO item_images (
                    image_pk, item_fk, image_path, image_created_at
                ) VALUES (%s,%s,%s,%s)
            """, (str(uuid.uuid4()), pk, path, ts))

        db.commit()
        flash(get_text("save_changes_success"), "success")
        return redirect(url_for("admin_list_items", lang=lang))
    except Exception as ex:
        db.rollback()
        flash(str(ex), "error")
        return redirect(url_for("admin_edit_item", lang=lang, pk=pk))
    finally:
        cursor.close()
        db.close()


@app.post("/<lang>/account/edit")
@login_required
def save_profile(lang):
    try:
        db, cursor      = x.db()
        new_username    = x.validate_user_username()
        new_name        = x.validate_user_name()
        new_last        = x.validate_user_last_name()
        new_email       = x.validate_user_email()

        cursor.execute("""
            UPDATE users
               SET user_username   = %s,
                   user_name       = %s,
                   user_last_name  = %s,
                   user_email      = %s,
                   user_updated_at = %s
             WHERE user_pk        = %s
        """, (
            new_username,
            new_name,
            new_last,
            new_email,
            int(time.time()),
            session["user"]["user_pk"]
        ))
        db.commit()
        session["user"].update({
            "user_username": new_username,
            "user_name": new_name,
            "user_last_name": new_last,
            "user_email": new_email
        })
        flash(get_text("profile_updated"))
        return redirect(url_for("profile", lang=lang))
    except Exception as ex:
        if "db" in locals(): db.rollback()
        flash(str(ex))
        return redirect(url_for("edit_profile", lang=lang))
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


@app.get("/<lang>/account/password")
@login_required
def change_pw(lang):
    return render_template("page_change_pw.html", title=get_text("change_password"), lang=lang)


@app.post("/<lang>/account/password")
@login_required
def save_pw(lang):
    try:
        db, cursor = x.db()
        user       = session["user"]

        current_pw = request.form.get("current_password", "").strip()
        new_pw     = request.form.get("new_password", "").strip()
        confirm_pw = request.form.get("confirm_password", "").strip()

        if not check_password_hash(user["user_password"], current_pw):
            raise Exception(get_text("wrong_current_password"))
        if new_pw != confirm_pw:
            raise Exception(get_text("passwords_do_not_match"))

        request.form = request.form.copy()
        request.form["user_password"] = new_pw
        x.validate_user_password()

        hashed = generate_password_hash(new_pw)
        cursor.execute("""
            UPDATE users
               SET user_password   = %s,
                   user_updated_at = %s
             WHERE user_pk        = %s
        """, (hashed, int(time.time()), user["user_pk"]))
        db.commit()

        flash(get_text("password_changed"), "success")
        return redirect(url_for("profile", lang=lang))
    except Exception as ex:
        if "db" in locals(): db.rollback()
        return render_template("page_change_pw.html", title=get_text("change_password"), error_message=str(ex), lang=lang)
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


@app.get("/<lang>/account/delete")
@login_required
def request_delete_profile(lang):
    return render_template("page_request_delete_profile.html", title=get_text("request_delete_profile"))


@app.post("/<lang>/account/delete")
@login_required
def do_delete_profile(lang):
    try:
        db, cursor = x.db()
        ts         = int(time.time())
        cursor.execute("""
            UPDATE users
               SET user_deleted_at = %s
             WHERE user_pk        = %s
        """, (ts, session["user"]["user_pk"]))
        db.commit()

        session.clear()
        flash(get_text("profile_deleted"))
        return redirect(url_for("page_index", lang=lang))
    except Exception as ex:
        if "db" in locals(): db.rollback()
        flash(str(ex))
        return redirect(url_for("request_delete_profile", lang=lang))
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


@app.patch("/<lang>/admin/users/<pk>/block")
@admin_required
def block_user(lang, pk):
    try:
        db, cursor = x.db()
        ts         = int(time.time())
        cursor.execute("UPDATE users SET user_blocked_at = %s WHERE user_pk = %s", (ts, pk))
        db.commit()
        return redirect(url_for("admin_list_users", lang=lang))
    except Exception as ex:
        ic(ex)
        return "Systemfejl", 500
    finally:
        cursor.close()
        db.close()


@app.get("/<lang>/signup")
def show_signup(lang):
    if session.get("user"):
        return redirect(url_for("profile", lang=lang))
    session.pop("verify_email", None)
    session.pop("verify_code", None)
    return render_template("page_signup.html", title=get_text("signup"), error_message="", old_values={}, lang=lang)


@app.post("/<lang>/signup")
def signup(lang):
    try:
        user_username     = x.validate_user_username()
        user_name         = x.validate_user_name()
        user_last_name    = x.validate_user_last_name()
        user_email        = x.validate_user_email()
        user_password     = x.validate_user_password()

        hashed_pw         = generate_password_hash(user_password)
        ts                = int(time.time())
        verification_code = str(randint(100000, 999999))

        db, cursor = x.db()
        cursor.execute("""
            INSERT INTO users (
                user_username, user_name, user_last_name,
                user_email, user_password, user_created_at,
                user_updated_at, user_deleted_at,
                user_verification_code, user_is_verified, user_role
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 0, 0, %s, 0, 'user'
            )
        """, (
            user_username, user_name, user_last_name,
            user_email, hashed_pw, ts,
            verification_code
        ))
        db.commit()

        session["verify_email"] = user_email
        session["verify_code"]  = verification_code
        x.send_email_verification(user_email, verification_code)

        flash(get_text("verification_sent"))
        return redirect(url_for("verify", lang=lang))
    except Exception as ex:
        if "db" in locals(): db.rollback()
        return render_template("page_signup.html", title=get_text("signup"), error_message=str(ex), old_values=request.form.to_dict(), lang=lang)
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


@app.get("/<lang>/verify")
def verify(lang):
    return render_template("page_verify.html", title=get_text("verify"), error_message="", lang=lang)


@app.post("/<lang>/verify")
def do_verify(lang):
    code          = request.form.get("code", "").strip()
    email         = session.get("verify_email")
    expected_code = session.get("verify_code")

    if not email or code != expected_code:
        return render_template("page_verify.html", title=get_text("verify"), error_message=get_text("invalid_code"), lang=lang)

    db, cursor = x.db()
    cursor.execute("""
        UPDATE users
           SET user_is_verified = 1,
               user_updated_at  = %s
         WHERE user_email      = %s
    """, (int(time.time()), email))
    db.commit()
    cursor.close(); db.close()

    session.pop("verify_email"); session.pop("verify_code")
    flash(get_text("verified_success"))
    return redirect(url_for("show_login", lang=lang))


@app.get("/<lang>/forgot")
def forgot_password(lang):
    return render_template("page_forgot_password.html", title=get_text("forgot_password"), lang=lang)


@app.post("/<lang>/forgot")
def send_reset(lang):
    try:
        user_email = x.validate_user_email()

        db, cur = x.db()
        cur.execute("SELECT user_pk FROM users WHERE user_email=%s", (user_email,))
        if not cur.fetchone():
            flash(get_text("reset_email_sent"), "info")
            return redirect(url_for("forgot_password", lang=lang))

        token = str(uuid.uuid4())
        cur.execute("UPDATE users SET user_reset_token = %s WHERE user_email = %s", (token, user_email))
        db.commit()

        x.send_email_password_reset(user_email, token)
        flash(get_text("reset_email_sent"), "info")
        return redirect(url_for("show_login", lang=lang))
    except Exception as ex:
        db.rollback()
        flash(str(ex), "error")
        return redirect(url_for("forgot_password", lang=lang))
    finally:
        cur.close(); db.close()


@app.get("/<lang>/reset/<token>")
def show_reset(lang, token):
    db, cur = x.db()
    cur.execute("SELECT user_email FROM users WHERE user_reset_token=%s", (token,))
    row = cur.fetchone()
    cur.close(); db.close()

    if not row:
        flash(get_text("reset_link_invalid"), "error")
        return redirect(url_for("forgot_password", lang=lang))

    return render_template("page_reset_password.html", title=get_text("reset_password"), token=token, lang=lang)


@app.post("/<lang>/reset/<token>")
def reset_password(lang, token):
    try:
        db, cur = x.db()
        cur.execute("SELECT user_email FROM users WHERE user_reset_token=%s", (token,))
        row = cur.fetchone()
        if not row:
            raise Exception(get_text("reset_link_invalid"))
        email = row["user_email"]

        new_pw     = request.form.get("user_password", "").strip()
        confirm_pw = request.form.get("confirm_password", "").strip()
        if new_pw != confirm_pw:
            raise Exception(get_text("passwords_do_not_match"))

        request.form = request.form.copy()
        request.form["user_password"] = new_pw
        x.validate_user_password()

        hashed = generate_password_hash(new_pw)
        cur.execute("""
            UPDATE users
               SET user_password    = %s,
                   user_updated_at  = %s,
                   user_reset_token = NULL
             WHERE user_email      = %s
        """, (hashed, int(time.time()), email))
        db.commit()

        flash(get_text("password_changed"), "success")
        return redirect(url_for("show_login", lang=lang))
    except Exception as ex:
        db.rollback()
        return render_template("page_reset_password.html", title=get_text("reset_password"), token=token, error_message=str(ex), lang=lang)
    finally:
        cur.close(); db.close()


# ----------------------------------------
# WSGI entrypoint (PythonAnywhere)
# ----------------------------------------
application = app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
