

from flask import request, url_for, session
import mysql.connector
import re

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

# import mysql.connector
# import re
# import uuid
# from datetime import datetime, timedelta
# from flask import request
# from werkzeug.security import generate_password_hash, check_password_hash
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# def db():
#     """
#     Return a new MySQL database connection and cursor (dictionary=True).
#     """
#     connection = mysql.connector.connect(
#         host="mysql",
#         user="root",
#         password="password",
#         database="company"
#     )
#     cursor = connection.cursor(dictionary=True)
#     return connection, cursor

# USERNAME_MIN, USERNAME_MAX = 2, 20
# NAME_MIN, NAME_MAX = 2, 20
# PASSWORD_MIN, PASSWORD_MAX = 6, 20
# EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
# PAGE_NUMBER_REGEX = r"^[1-9][0-9]*$"

# def validate_string(field_name, min_length, max_length):
#     """
#     Validate that a form field is between min_length and max_length.
#     Returns the stripped value or raises Exception.
#     """
#     value = request.form.get(field_name, "").strip()
#     if not (min_length <= len(value) <= max_length):
#         raise Exception(f"{field_name.replace('_', ' ').capitalize()} must be {min_length}-{max_length} characters")
#     return value

# def validate_user_email():
#     """
#     Validate email format from form.
#     Returns the email or raises Exception.
#     """
#     validate_user_email = request.form.get("user_email", "").strip()
#     if not re.match(EMAIL_REGEX, email):
#         raise Exception("Invalid email format")
#     return validate_user_email

# def validate_user_password(min_length=PASSWORD_MIN, max_length=PASSWORD_MAX):
#     """
#     Validate password length.
#     Returns the password or raises Exception.
#     """
#     password = request.form.get("user_password", "").strip()
#     if not (min_length <= len(password) <= max_length):
#         raise Exception(f"Password must be {min_length}-{max_length} characters")
#     return password

# def validate_page_number(page_number):
#     """
#     Validate that page_number matches PAGE_NUMBER_REGEX.
#     Returns int(page_number) or raises Exception.
#     """
#     if not re.match(PAGE_NUMBER_REGEX, str(page_number)):
#         raise Exception("Invalid page number")
#     return int(page_number)

# def validate_login_form():
#     """
#     Validate login form and return (email, password)
#     """
#     email = validate_email()
#     password = validate_password()
#     return email, password

# def validate_signup_form():
#     """
#     Validate signup form and return (username, name, last_name, email, password)
#     """
#     user_username = validate_string("user_username", USERNAME_MIN, USERNAME_MAX)
#     user_name = validate_string("user_name", NAME_MIN, NAME_MAX)
#     user_last_name = validate_string("user_last_name", NAME_MIN, NAME_MAX)
#     user_email = validate_email()
#     user_password = validate_password()
#     return user_username, user_name, user_last_name, user_email, user_password


SENDER_EMAIL = "michelleenoea@gmail.com"
SENDER_NAME = "LoppePusher"
APP_PASSWORD = "tsaf imag yrkq udvu"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def _send_email(to_email, subject, html_body):
    """
    Internal helper to send an HTML email.
    """
    message = MIMEMultipart()
    message["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(message)

def send_email_verification(to_email, code):
    """
    Send account verification email with code.
    """
    subject = "Verify your LoppePusher account"
    body = f"""
    <p>To verify your account, enter the following code:</p>
    <h2>{code}</h2>
    <p>– LoppePusher Team</p>
    """
    _send_email(to_email, subject, body)

def send_email_password_reset(to_email, reset_token):
    """
    Send password reset email med et fuldt link til /<lang>/reset/<token>
    """
    lang = session.get("lang", "da")
    # url_for med _external=True bruger request.host_url (fx http://127.0.0.1:5000/)
    reset_link = url_for(
        'reset_password',      # navnet på din POST-route-funktion
        lang=lang,
        token=reset_token,
        _external=True
    )

    subject = "Reset your LoppePusher password"
    body = f"""
    <p>Klik på linket herunder for at nulstille din adgangskode (udløber om 1 time):</p>
    <p><a href="{reset_link}">{reset_link}</a></p>
    """
    _send_email(to_email, subject, body)

def send_email_block_notification(to_email, is_blocked):  # is_blocked: 1=blokeret, 0=aktiv
    """
    Notify user that their account has been blocked/unblocked.
    """
    status = "blokeret" if is_blocked else "genåbnet"
    subject = f"Din LoppePusher-konto er {status}"
    body = f"""
    <p>Din konto er nu {status} af en administrator.</p>
    """
    _send_email(to_email, subject, body)

def send_email_item_notification(to_email, item_pk, new_status):
    """
    Notify a user that one of their items has been blocked/unblocked.
    """
    subject = f"Dit item #{item_pk} er nu {new_status}"
    body = f"""
    <p>Item med ID #{item_pk} er blevet sat til status: {new_status}.</p>
    """
    _send_email(to_email, subject, body)

def validate_user_email():
    return validate_email()




##############################
def db():
    db = mysql.connector.connect(
        host = "mysql",      # Replace with your MySQL server's address or docker service name "mysql"
        user = "root",  # Replace with your MySQL username
        password = "password",  # Replace with your MySQL password
        database = "company"   # Replace with your MySQL database name
    )
    cursor = db.cursor(dictionary=True)
    return db, cursor


##############################
USER_USERNAME_MIN = 2
USER_USERNAME_MAX = 20
USER_USERNAME_REGEX = f"^.{{{USER_USERNAME_MIN},{USER_USERNAME_MAX}}}$"
def validate_user_username():
    error = f"username {USER_USERNAME_MIN} to {USER_USERNAME_MAX} characters"
    user_username = request.form.get("user_username", "").strip()
    if not re.match(USER_USERNAME_REGEX, user_username): raise Exception(error)
    return user_username


##############################
USER_NAME_MIN = 2
USER_NAME_MAX = 20
USER_NAME_REGEX = f"^.{{{USER_NAME_MIN},{USER_NAME_MAX}}}$"
def validate_user_name():
    error = f"name {USER_NAME_MIN} to {USER_NAME_MAX} characters"
    user_name = request.form.get("user_name", "").strip()
    if not re.match(USER_NAME_REGEX, user_name): raise Exception(error)
    return user_name


##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20
USER_LAST_NAME_REGEX = f"^.{{{USER_LAST_NAME_MIN},{USER_LAST_NAME_MAX}}}$"
def validate_user_last_name():
    error = f"last name {USER_LAST_NAME_MIN} to {USER_LAST_NAME_MAX} characters"
    user_last_name = request.form.get("user_last_name", "").strip()
    if not re.match(USER_LAST_NAME_REGEX, user_last_name): raise Exception(error)
    return user_last_name

##############################
USER_EMAIL_REGEX = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
def validate_user_email():
    error = f"Invalid email"
    user_email = request.form.get("user_email", "").strip()
    if not re.match(USER_EMAIL_REGEX, user_email): raise Exception(error)
    return user_email

##############################
USER_PASSWORD_MIN = 6
USER_PASSWORD_MAX = 20
USER_PASSWORD_REGEX = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"
def validate_user_password():
    error = f"password {USER_PASSWORD_MIN} to {USER_PASSWORD_MAX} characters"
    user_password = request.form.get("user_password", "").strip()
    if len(user_password) < USER_PASSWORD_MIN: raise Exception(error)
    if len(user_password) > USER_PASSWORD_MAX: raise Exception(error)
    return user_password

##############################
PAGE_NUMBER_REGEX = "^[1-9][0-9]*$"
def validate_page_number(page_number):
    error = "page number not valid"
    if not re.match(PAGE_NUMBER_REGEX, page_number): raise Exception(error)
    return int(page_number)


# --- øverst i x.py ---
import os, re, uuid
from flask import request, current_app

ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]
MAX_FILE_SIZE      = 5 * 1024 * 1024
MAX_FILES          = 5
MIN_FILES          = 3

# ---------- FELT-VALIDERINGER ----------
ITEM_NAME_MIN, ITEM_NAME_MAX = 2, 255

def _match(field, regex, err):
    v = request.form.get(field, "").strip()
    if not re.match(regex, v):
        raise Exception(err)
    return v

def validate_item_name():
    return _match("item_name",
                  rf"^.{{{ITEM_NAME_MIN},{ITEM_NAME_MAX}}}$",
                  "item name 2-255 chars")

def validate_item_address():
    return _match("item_address", r"^.{2,100}$", "address 2-100 chars")

def validate_item_description():
    return _match("item_description", r"^.{2,1000}$",
                  "description 2-1000 chars")

def validate_item_price():
    p = request.form.get("item_price", "").strip()
    if p and not re.match(r"^\d{1,9}(\.\d{1,2})?$", p):
        raise Exception("invalid price")
    return p
def validate_item_lat():
    # midlertidig: ingen format-tjek
    return request.form.get("item_lat", "").strip().replace(",", ".")

def validate_item_lon():
    # midlertidig: ingen format-tjek
    return request.form.get("item_lon", "").strip().replace(",", ".")



## Konstanter du bruger:
MIN_FILES = 1     # eller 3 hvis du ønsker min. 3 billeder ved oprettelse
MAX_FILES = 5
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# --- x.py ---
from flask import request, current_app
import os, uuid

# MIN_FILES = 3
# MAX_FILES = 5
# MAX_FILE_SIZE = 5 * 1024 * 1024  # e.g. 5 MB per file
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def validate_item_images(field="files", optional=False):

    files = [f for f in request.files.getlist(field) if f and f.filename]
    # no files at all
    if not files:
        if optional:
            return []
        else:
            raise Exception("upload_at_least_three")

    # enforce minimum only when not optional
    if not optional and len(files) < MIN_FILES:
        raise Exception("upload_at_least_three")
    if len(files) > MAX_FILES:
        raise Exception("upload_max_five")

    saved = []
    upload_dir = current_app.config["UPLOAD_FOLDER"]

    for f in files:
        # check file size
        data = f.read()
        if len(data) > MAX_FILE_SIZE:
            raise Exception("upload_file_too_large")
        f.seek(0)

        # extension check
        ext = os.path.splitext(f.filename)[1].lstrip(".").lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise Exception("upload_extension_not_allowed")

        # save with uuid-based name
        new_name = f"{uuid.uuid4().hex}.{ext}"
        f.save(os.path.join(upload_dir, new_name))
        saved.append(new_name)

    return saved






# ##############################
# def send_email(user_name, user_last_name):
#     try:
#         # Create a gmail
#         # Enable (turn on) 2 step verification/factor in the google account manager
#         # Visit: https://myaccount.google.com/apppasswords

#         # Email and password of the sender's Gmail account
#         sender_email = ""
#         password = ""  # If 2FA is on, use an App Password instead

#         # Receiver email address
#         receiver_email = ""
        
#         # Create the email message
#         message = MIMEMultipart()
#         message["From"] = "My company name"
#         message["To"] = ""
#         message["Subject"] = "Welcome"

#         # Body of the email
#         body = f"Thank you {user_name} {user_last_name} for signing up. Welcome."
#         # body = f"""To verify your account, please <a href="http://127.0.0.1/verify/{user_verification_key}">click here</a>"""
#         message.attach(MIMEText(body, "html"))

#         # Connect to Gmail's SMTP server and send the email
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()  # Upgrade the connection to secure
#             server.login(sender_email, password)
#             server.sendmail(sender_email, receiver_email, message.as_string())
#         ic("Email sent successfully!")

#         return "email sent"
       
#     except Exception as ex:
#         ic(ex)
#         raise Exception("cannot send email")
#     finally:
#         pass
