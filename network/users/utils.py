from flask import url_for, current_app
from network import mail
from flask_login import current_user
import secrets
import os
from PIL import Image
from flask_mail import Message

def save_image(form_image):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(current_app.root_path, 'static/profile_pics', image_fn)
    output_size = (300,300)
    img = Image.open(form_image)
    img.thumbnail(output_size)
    img.save(image_path)
    prev_image = os.path.join(current_app.root_path, 'static/profile_pics', current_user.profile_image)
    if os.path.exists(prev_image):
        os.remove(prev_image)
    return image_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Сброс пароля', sender='noreply@flask-network.com',
                    recipients=[user.email])
    msg.body = f""" Для сброса пароля перейдите по следующей ссылке:
{url_for('users.reset_token', token=token, _external=True)}

Если вы не запрашивали сброс пароля, просто проигнорируйте это сообщение.
    """
    mail.send(msg)
