from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required
from .db import get_db

bp = Blueprint('tag', __name__)


def get_post_tags(post_id:int):

    tags = get_db().execute(
        'SELECT *'
        ' FROM tag'
        ' WHERE post_id = ?',
        (post_id,)
    ).fetchall()

    return tags


def get_posts_per_tag(tag_text:str):
    posts = get_db().execute(
        'SELECT *'
        ' FROM tag INNER JOIN post ON tag.post_id = post.id INNER JOIN user ON user.id=author_id'
        ' WHERE tag_text=?',
        (tag_text,)
    ).fetchall()
    
    return posts


def get_tags():
    db = get_db()
    tags = db.execute('SELECT  tag_text, COUNT(tag_text) AS count'
            ' FROM tag' 
            ' GROUP BY tag_text',
            ).fetchall()
    return tags


def delete_tag(post_id:int, tag_text:str):
    db = get_db()
    db.execute(
        'DELETE from tag WHERE post_id=? AND tag_text=?',(post_id,tag_text)
    )
    db.commit()



# Routes 

@bp.route('/<int:post_id>/add_tag', methods=('POST',))
@login_required
def add_tag(post_id):
    tag_text:str = request.form['tag_text']
    print(tag_text)
    db = get_db()
    db.execute(
        'INSERT INTO tag (tag_text, user_id, post_id)'
        ' values(?,?,?)',
        (tag_text,g.user['id'],post_id )

    )
    db.commit()
    return redirect(f"/blog/{post_id}")

@bp.route('/<int:post_id>/remove_tag/<string:tag_text>', methods=('GET',))
def delete_tag(post_id:int, tag_text:str):
    db = get_db()
    db.execute(
        'DELETE from tag WHERE post_id=? AND tag_text=?',(post_id,tag_text)
    )
    db.commit()
    return redirect(f"/blog/{post_id}")


@bp.route('/tag/<string:tag_text>', methods=('GET',))
def show_posts_by_tag(tag_text):
    posts = get_posts_per_tag(tag_text=tag_text)
    print('posts', posts)
    return render_template('tag/list.html', posts=posts, tag_text=tag_text)


@bp.route('/tags', methods=('GET',))
def show_all_tags():
    tags = get_tags()
    return render_template('tag/list_all.html', tags=tags) 


@bp.route('/api/tag', methods=('GET',))
def api_all_tags():
    tags = get_tags()
    tags = [dict(tag) for tag in tags]
    for tag in tags:
        tag['posts'] = [dict(post)['title'] for post in get_posts_per_tag(tag['tag_text'])]
    return tags

@bp.route('/api/tag/<string:tag_text>', methods=('GET',))
def api_posts_per_tag(tag_text):
    posts = get_posts_per_tag(tag_text=tag_text)
    posts = [dict(post) for post in posts]
    return posts