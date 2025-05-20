from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
from .comment import get_comments
from .tag import get_post_tags

bp = Blueprint('blog', __name__)


def get_posts():
    posts = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, likes'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
        ).fetchall()

    return posts


def get_post(post_id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, likes'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (post_id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


def search_posts_by_title_or_tag(search_term:str):
    db=get_db()
    posts = db.execute(
        'SELECT DISTINCT post.id, title, body, post.created, author_id, username, likes tag_text'
        ' FROM post INNER JOIN user ON post.author_id=user.id INNER JOIN tag ON post.id=tag.post_id'
        ' WHERE LOWER(post.title) LIKE LOWER(?) OR LOWER(tag_text) LIKE LOWER(?)',
        (f'%{search_term}%',f'%{search_term}%',)
    ).fetchall()
    return posts

@bp.route('/',methods=('GET','POST'))
def index():
    if request.method=='GET':
        posts = get_posts()
        return render_template('blog/index.html', posts=posts)
    if request.method=='POST':
        search_term:str = str(request.form['search_term'])
        posts = search_posts_by_title_or_tag(search_term=search_term)
        print(posts)
        return render_template('blog/index.html', posts=posts)
    else:
        return "<p>method not allowed</p>"


@bp.route('/blog/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
  

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, likes)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], 0)
            )
            db.commit()
            print(title)
            print(body)
            print(g.user['id'])
            
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/blog/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/blog/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/blog/<int:post_id>', methods=('GET',))
def view_single_post(post_id):
    
    post = get_post(post_id,check_author=False)
    comments = get_comments(post_id=post_id)
    tags = get_post_tags(post_id=post_id)

    return render_template('blog/blog.html', post=post, comments=comments, tags=tags)


@bp.route('/api/post', methods=('GET',))
def api_posts():
    posts = get_posts()
    return [dict(post) for post in posts]

@bp.route('/api/post/<int:post_id>', methods=('GET',))
def api_post(post_id):
    post = get_post(post_id=post_id, check_author=False)
    return dict(post)