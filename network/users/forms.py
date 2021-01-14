from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import Email, Length, EqualTo, InputRequired, ValidationError
from flask_wtf.file import FileAllowed
from network.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[InputRequired(), Length(min=2,max=20)])
    email = StringField('Email', validators=[Email(), InputRequired()])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[InputRequired(), Length(min=6), EqualTo('password')])

    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Имя пользователя занято')
    
    def validate_email(self, email):
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email уже используется')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email(), InputRequired()])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=6)])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class EditProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[Length(min=2,max=20)])
    email = StringField('Email', validators=[Email(), Length(min=2,max=40)])
    about = StringField('О себе', validators=[Length(min=0, max=140)])
    profile_image = FileField('Аватар', validators=[    
        FileAllowed(['jpg', 'png', 'gif', 'bmp'], 'Только картинки!')
    ])
    submit = SubmitField('Изменить')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Имя пользователя занято')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email уже используется')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[Email(), InputRequired()])
    submit = SubmitField('Запросить сброс пароля')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Нет пользователя с таким email')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[InputRequired(), Length(min=6), EqualTo('password')])
    submit = SubmitField('Изменить пароль')
