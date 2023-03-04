from flask import Flask, render_template, request
from flask_hcaptcha import hCaptcha
from datetime import datetime
from os import environ
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import make_msgid, localtime, format_datetime

app = Flask(__name__)
app.config['HCAPTCHA_SITE_KEY'] = environ.get("HCAPTCHA_SITE_KEY", "")
app.config['HCAPTCHA_SECRET_KEY'] = environ.get("HCAPTCHA_SECRET_KEY", "")
hcaptcha = hCaptcha(app)



@app.route('/', methods=["GET", "POST"])
def index():
        if request.method == "GET":
                return render_template("index.html", form_data=None)
        elif request.method == "POST":
                if hcaptcha.verify():
                        my_message = EmailMessage()
                        my_message['Subject'] = "Kontaktformular Nachricht"
                        my_message['From'] = environ.get("SMTP_FROM", "")
                        my_message['To'] = environ.get("SMTP_RCPT", "")
                        my_message['Message-Id'] = make_msgid(domain=environ.get("SMTP_SERVER", ""))
                        my_message['Date'] = format_datetime(localtime())
                        my_message.set_content(f"""Es gab eine neue Kontaktformular Nachricht:

Typ: {request.form['type']}
Name: {request.form['name']}
E-Mail: {request.form['email']}
Terminidee (falls vorhanden): {request.form['date']}
Nachricht:
{request.form['message']}""")

                        copy_message = EmailMessage()
                        copy_message['Subject'] = "Deine Kontaktformular Nachricht"
                        copy_message['From'] = environ.get("SMTP_FROM", "")
                        copy_message['To'] = request.form['email']
                        copy_message['Message-Id'] = make_msgid(domain=environ.get("SMTP_SERVER", ""))
                        copy_message['Date'] = format_datetime(localtime())
                        copy_message.set_content(f"""Hier eine Kopie deiner Kontaktformular Nachricht:

Typ: {request.form['type']}
Name: {request.form['name']}
E-Mail: {request.form['email']}
Terminidee (falls vorhanden): {request.form['date']}
Nachricht:
{request.form['message']}

Ich werde dir schnellstmöglich eine Antwort senden. Bis dahin,
- Christy""")
                        ssl_context = ssl.create_default_context()
                        with smtplib.SMTP_SSL(environ.get("SMTP_SERVER", ""), 465, context=ssl_context) as server:
                                email_user = environ.get("SMTP_FROM", "")
                                email_password = environ.get("SMTP_PASS", "")
                                server.login(email_user, email_password)
                                server.send_message(my_message)
                                server.send_message(copy_message)
                        return render_template("send.html", form_data=request.form)
                else:
                        return render_template("index.html", captcha_error=True, form_data=request.form)

if __name__ == "__main__":
        app.run(host="0.0.0.0", debug=True)
