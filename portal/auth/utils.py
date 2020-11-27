from flask import url_for, current_app
from flask_mail import Message
from portal import mail

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    msg.body = f'''Untuk mereset password, Silahkan klik link ini:
{url_for('auth.reset_token', token=token, _external=True)}
Jika Anda tidak ingin mengganti password, abaikan pesan ini.
'''
    mail.send(msg)