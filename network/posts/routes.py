from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, current_app
from network import db
from .forms import (PostForm, CommentForm)
from network.models import Comment, Post
from flask_login import current_user, login_required
from .utils import save_post_image
import os

posts = Blueprint('posts', __name__)

@posts.route('/post/<int:post_id>', methods=["GET", "POST"])
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if post.is_hidden and post.author != current_user:
            flash('Этот пост скрытый.', 'warning')
            return redirect(url_for('main.blog'))
    comments = Comment.query.filter_by(parent_post=post)
    form = CommentForm()
    # Form for comment creation
    if form.validate_on_submit():
        if form.comment_image.data:
            comment_pic = save_post_image(form.comment_image.data)
            new_comment = Comment(comment_content = form.comment_content.data, comment_image = comment_pic, author = current_user, parent_post=post)
        else:
            new_comment = Comment(comment_content = form.comment_content.data, author = current_user, parent_post=post)
        db.session.add(new_comment)
        db.session.commit()
        flash('Ваш коммент по идее сохранен, проверяйте', 'info')
        return redirect(request.referrer)
            
    return render_template('post_detail.html', title=post.title, post=post, form=form, comments=comments)

@posts.route('/comment/<int:comment_id>/update', methods=["GET", "POST"])
@login_required
def comment_update(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        abort(403)
    try:
        Post.query.get_or_404(comment.parent_post.id)
    except:
        abort(404)
    form = CommentForm()
    if form.validate_on_submit():
        if form.comment_image.data:
            comment_pic = save_post_image(form.comment_image.data)
            comment.comment_image = comment_pic
        else:
            comment.comment_image = None
        comment.comment_content = form.comment_content.data
        comment.is_edited = True
        db.session.commit()
        flash('Комментарий изменен!', 'success')
        return redirect(request.referrer)
    elif request.method == "GET":
        form.comment_content.data = comment.comment_content
    return render_template('comment_update.html', title=comment.author.username, comment=comment, form=form)


@posts.route('/post/<int:post_id>/update', methods=["GET", "POST"])
@login_required
def post_update(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        if form.post_image.data:
            post_pic = save_post_image(form.post_image.data)
            post.post_image = post_pic
        else:
            post.post_image = None
        post.title = form.title.data
        post.content = form.content.data
        post.is_hidden = form.hidden.data
        post.is_edited = True
        db.session.commit()
        flash('Пост изменен!', 'success')
        return redirect(request.referrer)
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        form.hidden.data = post.is_hidden
    return render_template('post_update.html', title=post.title, post=post, form=form)



@posts.route('/post/<int:post_id>/delete', methods=["POST"])
@login_required
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    post_image = os.path.join(current_app.root_path, 'static/post_pics', post.post_image)
    if os.path.exists(post_image):
        os.remove(post_image)
    db.session.delete(post)
    db.session.commit()
    flash('Пост был удален', 'success')
    return redirect(url_for('users.profile', username=current_user.username))


@posts.route('/comment/<int:comment_id>/delete', methods=["POST"])
@login_required
def comment_delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    redir_id = int(comment.parent_post.id)
    if comment.author != current_user:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Комментарий был удален', 'success')
    return redirect(url_for('users.post_detail', post_id=redir_id))