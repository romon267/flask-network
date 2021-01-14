from flask import current_app
from flask_login import current_user
import secrets
import os
from PIL import Image

def save_post_image(form_image): # Saves file with a new name, then
    random_hex = secrets.token_hex(8) # returns new name to store in database
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(current_app.root_path, 'static/post_pics', image_fn)
    output_size = (400,400)
    img = Image.open(form_image)
    img.thumbnail(output_size)
    img.save(image_path)
    return image_fn