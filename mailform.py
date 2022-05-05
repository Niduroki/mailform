from flask import Flask, render_template, request
from flask_hcaptcha import hCaptcha
from datetime import datetime
from os import environ
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import make_msgid, localtime, format_datetime

app = Flask(__name__)
app.config['HCAPTCHA_SITE_KEY'] = os.environ("HCAPTCHA_SITE_KEY", "")
app.config['HCAPTCHA_SECRET_KEY'] = os.environ("HCAPTCHA_SECRET_KEY", "")
hcaptcha = hCaptcha(app)



@app.route('/', methods=["GET", "POST"])
def index():
        if request.method == "GET":
                return render_template("index.html", form_data=None)
        elif request.method == "POST":
                if hcaptcha.verify():
                        message = EmailMessage()
                        message['Subject'] = "Kontaktformular Nachricht"
                        message['From'] = os.environ("SMTP_FROM", "")
                        message['To'] = os.environ("SMTP_RCPT", "")
                        message['Message-Id'] = make_msgid(domain=os.environ("SMTP_SERVER", ""))
                        message['Date'] = format_datetime(localtime())
                        message.set_content(f"""Es gab eine neue Kontaktformular Nachricht:

Typ: {request.form['type']}
Name: {request.form['name']}
E-Mail: {request.form['email']}
Terminidee (falls vorhanden): {request.form['date']}
Nachricht:
{request.form['message']}""")
                        ssl_context = ssl.create_default_context()
                        with smtplib.SMTP_SSL(os.environ("SMTP_SERVER", ""), 465, context=ssl_context) as server:
                                email_user = os.environ("SMTP_FROM", "")
                                email_password = os.environ("SMTP_PASS", "")
                                server.login(email_user, email_password)
                                server.send_message(message)
                        return render_template("send.html", form_data=request.form)
                else:
                        return render_template("index.html", captcha_error=True, form_data=request.form)

if __name__ == "__main__":
        app.run(host="0.0.0.0", debug=True)