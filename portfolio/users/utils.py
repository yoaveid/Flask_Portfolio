from flask import url_for
from flask_mail import Message
from portfolio import mail

def send_reset_email(user):
    token = user.get_rest_token()
    msg = Message('Password Reset Reaquest', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then ignore this email     
'''
    mail.send(msg)


