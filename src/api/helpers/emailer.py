import smtplib
from email.message import EmailMessage
import api.settings


class Emailer:
    def __init__(self):
        self.send_mail = api.settings.SEND_MAIL
        self.app_pass = api.settings.APP_PASS_GMAIL

    def send_email(self, to_email, subject, body):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.send_mail
        msg["To"] = to_email

        msg.set_content("Twoja przeglądarka nie obsługuje HTML.")
        msg.add_alternative(body, subtype="html")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.send_mail, self.app_pass)
            smtp.send_message(msg)
