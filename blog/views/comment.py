from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required
from .db import get_db

bp = Blueprint('comment', __name__)


def get_comments(post_id):

    comments = get_db().execute(
        'SELECT *'
        ' FROM comment JOIN user ON user_id = user.id'
        ' WHERE post_id = ?'
        ' ORDER BY created DESC',
        (post_id,)
    ).fetchall()

    return comments


@bp.route('/<int:post_id>/add_comment', methods=('POST','GET'))
@login_required
def add_comment(post_id):
    title:str = request.form['title']
    body:str = request.form['body']

    db = get_db()
    db.execute(
        'INSERT INTO comment (title, body, user_id, post_id)'
        ' values(?,?,?,?)',
        (title,body,g.user['id'],post_id )

    )
    db.commit()
    return redirect(f"/blog/{post_id}")


@bp.route('/<int:post_id>/delete_comment/<int:comment_id>', methods=('POST','GET'))
@login_required
def delete_comment(comment_id, post_id):

    db = get_db()
    db.execute('DELETE from comment WHERE id=?',(comment_id,)) 
    db.commit()
    return redirect(f"/blog/{post_id}")