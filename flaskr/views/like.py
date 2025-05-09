from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
from .blog import get_post

bp = Blueprint('like', __name__)


def has_been_liked(post_id) -> bool:
    db = get_db()
    liked = db.execute(
        'SELECT *'
        ' FROM like'
        ' WHERE post_id = ? AND user_id = ?',
        (post_id,g.user['id'])
    ).fetchone()

    if liked is None:
        return False
    return True


@bp.route('/blog/<int:post_id>/like', methods=('GET',))
@login_required
def like_post(post_id):

    if has_been_liked(post_id=post_id):
        print('blog already liked')
        return redirect(f"/blog/{post_id}") 


    post = get_post(post_id,check_author=False) 
    n_likes:int = post['likes']+1
    db = get_db()
    db.execute(
        'INSERT INTO like (post_id, user_id)'
        ' VALUES(?, ?)',(post_id,g.user['id'])
    )
    db.execute(
        'UPDATE post SET likes = ?'
        ' WHERE id = ?',
        (n_likes, post_id)
    )
    db.commit()

    return redirect(f"/blog/{post_id}")


@bp.route('/blog/<int:post_id>/dislike', methods=('GET',))
@login_required
def dislike_post(post_id):

    if has_been_liked(post_id=post_id) == False:
        print('cannot dislike post')
        return redirect(f"/blog/{post_id}") 

    post = get_post(post_id,check_author=False) 
    n_likes:int = max(post['likes']-1,0)
    print(n_likes)
    db = get_db()
    db.execute('DELETE from like WHERE post_id=? and user_id=?',(post_id,g.user['id']))
    db.execute(
        'UPDATE post SET likes = ?'
        ' WHERE id = ?',
        (n_likes, post_id)
    )
    db.commit()

    return redirect(f"/blog/{post_id}")