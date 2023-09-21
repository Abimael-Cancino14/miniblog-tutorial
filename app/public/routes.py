from flask import abort, render_template, current_app, url_for, redirect, request
from werkzeug.exceptions import NotFound
import logging
from flask_login import current_user
from .forms import CommentForm
from app.models import Comment

from app.models import Post
from . import public_bp

logger = logging.getLogger(__name__)

@public_bp.route("/")
def index():
#    current_app.logger.info('Mostrando los posts del blog')
#    logger.info(current_user.name)
    enterpage = request.args.get('page', 1)
    lim_page = request.args.get('lim', 3)
    logger.info(enterpage)  
    try:
        page = int(enterpage)
    except ValueError:
        page = 1

    try:
        limpage = int(lim_page)
    except ValueError:
        limpage = 3

    per_page = current_app.config['ITEMS_PER_PAGE']
    post_pagination = Post.all_paginated(page, limpage)
    return render_template("public/index.html", post_pagination=post_pagination, limpage=limpage)

@public_bp.route("/p/<string:slug>/", methods=['GET', 'POST'])
def show_post(slug):
#    logger.info('Mostrando un post')
#    logger.debug(f'Slug: {slug}')
    post = Post.get_by_slug(slug)
    if not post:
        logger.info(f'El post {slug} no existe')
        abort(404)
    form = CommentForm()
    if current_user.is_authenticated and form.validate_on_submit():
        content = form.content.data
        comment = Comment(content=content, user_id=current_user.id,
                          user_name=current_user.name, post_id=post.id)
        comment.save()
        return redirect(url_for('public.show_post', slug=post.title_slug))
    return render_template("public/post_view.html", post=post, form=form)

@public_bp.route("/error")
def show_error():
    res = 1 / 0
    posts = Post.get_all()
    return render_template("public/index.html", posts=posts)