import smtplib
from email.message import EmailMessage
import hashlib

# Set up email server 
gmail_user = ''
gmail_password = ''
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 465
server = smtplib.SMTP_SSL(host=SMTP_HOST, port=SMTP_PORT)
server.ehlo()
server.login(gmail_user, gmail_password)


def send_confirmation_letter(email):
    msg = EmailMessage()
    msg.set_content(f'''
        Please follow this link to confirm your email:\n
        http://localhost:5000/email_confirmation?email={email}&hash={hashlib.sha1((email + "salt").encode('utf-8')).hexdigest()}''')
    msg['subject'] = 'Please confirm your email'
    msg['To'] = email
    msg['From'] = gmail_user
    server.sendmail(gmail_user, [email], msg.as_string())
    return 0
    #except Exception as e:
    #    return {'errors': e}


