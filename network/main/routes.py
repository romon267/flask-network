from flask import Blueprint, render_template, url_for, redirect, request, abort, current_app
from network import db
from network.models import Post
from flask_login import current_user, login_required
from datetime import datetime

main = Blueprint('main', __name__)


@main.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
    db.session.commit()


@main.route("/")
@main.route("/home")
def landing():
    if current_user.is_authenticated:
        return redirect('blog')
    else:
        return render_template('about.html', title='О сайте')

@main.route("/about")
def about():
    return render_template('about.html', title='О сайте')


@main.route('/blog')
@login_required
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_hidden=False).order_by(Post.date_posted.desc()).paginate(page, per_page=current_app.config['POSTS_PER_PAGE'])
    user = current_user
    followed = user.followed.all()
    followers = user.followers.all()
    next_url = url_for('main.blog', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.blog', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('blog.html', posts=posts.items, user=user, followed = followed,
     followers = followers, next_url = next_url, prev_url=prev_url)


@main.route('/blog/followed')
@login_required
def blog_sorted():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, per_page=current_app.config['POSTS_PER_PAGE'])
    user = current_user
    followed = user.followed.all()
    followers = user.followers.all()
    next_url = url_for('main.blog_sorted', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.blog_sorted', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('blog.html', posts=posts.items, user=user, followed = followed,
     followers = followers, next_url=next_url, prev_url=prev_url)
