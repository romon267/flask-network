from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed


class PostForm(FlaskForm):
    title = StringField('Заголовок поста', validators=[DataRequired(),Length(min=2,max=80)])
    content = TextAreaField('Основной текст', validators=[DataRequired(), Length(min=2, max=300)])
    hidden = BooleanField('Скрытый пост')
    post_image = FileField('Картинка к посту', validators=[
        FileAllowed(['jpg', 'png', 'gif', 'bmp'], 'Только картинки!')
    ])
    submit = SubmitField('Отправить')


class CommentForm(FlaskForm):
    comment_content = TextAreaField('Коментарий', validators=[DataRequired(), Length(min=2, max=300)])
    comment_image = FileField('Картинка к коментарию', validators=[
        FileAllowed(['jpg', 'png', 'gif', 'bmp'], 'Только картинки!')
    ])
    submit = SubmitField('Отправить')