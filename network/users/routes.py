from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from network import db, bcrypt
from .forms import (EditProfileForm, RegistrationForm,
                             LoginForm, RequestResetForm, ResetPasswordForm)
from network.posts.forms import PostForm
from network.models import User, Post
from flask_login import login_user, logout_user, current_user, login_required
from .utils import save_image, send_reset_email
from network.posts.utils import save_post_image

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Вы зарегистрированы', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Регистрация', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.profile', username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Здравствуйте, {current_user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.landing'))
        else:
            flash('Неправильный пароль или email.', 'danger')
        return redirect(url_for('users.login'))
    return render_template('login.html', title='Логин', form=form)


@users.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.', 'success')
    return redirect(url_for('main.landing'))


@users.route('/profile/<username>', methods=["GET", "POST"])
@login_required
def profile(username):
    form = PostForm()
    if form.validate_on_submit():
        if form.post_image.data:
            post_pic = save_post_image(form.post_image.data)
            new_post = Post(title = form.title.data, content = form.content.data, is_hidden = form.hidden.data, post_image = post_pic, author = current_user)
        else:
            new_post = Post(title = form.title.data, content = form.content.data, is_hidden = form.hidden.data, author = current_user)
        db.session.add(new_post)
        db.session.commit()
        flash('Ваш пост по идее сохранен, проверяйте', 'info')
        return redirect(url_for('users.profile', username=current_user.username))
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    profile_image = url_for('static', filename=f'profile_pics/{user.profile_image}')
    posts = Post.query.filter_by(user_id = user.id).order_by(Post.date_posted.desc())
    visible_posts = Post.query.filter_by(user_id = user.id).filter_by(is_hidden = False).order_by(Post.date_posted.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'])
    followed = user.followed.all()
    followers = user.followers.all()
    
    next_url_visible = url_for('users.profile', page=visible_posts.next_num, username=user.username) \
        if visible_posts.has_next else None
    prev_url_visible = url_for('users.profile', page=visible_posts.prev_num, username=user.username) \
        if visible_posts.has_prev else None
    return render_template('profile.html', form=form, title=user.username, user=user, posts=posts,
     profile_image=profile_image, followed = followed, followers = followers, visible_posts = visible_posts.items,
     next_url_visible=next_url_visible, prev_url_visible=prev_url_visible)


@users.route('/edit_profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        
        if form.profile_image.data:
            current_user.profile_image = save_image(form.profile_image.data)
        
        current_user.username = form.username.data
        current_user.about = form.about.data
        current_user.email = form.email.data
        db.session.commit()
        
        flash('Изменения сохранены', 'success')
        return redirect(url_for('users.profile', username=current_user.username))
    username = current_user.username
    email = current_user.email
    about = current_user.about
    image = current_user.profile_image
    return render_template('edit_profile.html', title='Редактировать профиль', form=form, username=username ,email=email,about=about,image=image)


@users.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    if request.method == "POST":
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'Пользователь {username} не найден.', 'danger')
            return redirect(url_for('main.blog'))
        if user == current_user:
            flash('Вы не можете подписаться на себя!', 'danger')
            return redirect(url_for('users.profile', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'Вы подписались на {username}!', 'success')
        return redirect(url_for('users.profile', username=username))
    else:
        return redirect(url_for('main.blog'))



@users.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    if request.method == "POST":
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'Пользователь {username} не найден.', 'danger')
            return redirect(url_for('main.blog'))
        if user == current_user:
            flash('Вы не можете подписаться на себя!', 'danger')
            return redirect(url_for('users.profile', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'Вы отписались от {username}!', 'success')
        return redirect(url_for('users.profile', username=username))
    else:
        return redirect(url_for('main.blog'))


@users.route('/reset_password', methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Письмо с инструкциями по сбросу пароля было отпаравлено на указанный email.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title="Сброс пароля", form=form)


@users.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Токен для сброса пароля неверный или был просрочен', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password_hash = hashed_password
        db.session.commit()
        flash(f'Ваш пароль был изменен!', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_password.html', title='Сброс пароля', form=form)