from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required
from .db import get_db

bp = Blueprint('user', __name__)

def get_post_for_user_id(user_id):
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, likes'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.author_id = ?',
        (user_id,)
    ).fetchall()
    
    return posts

def get_user_from_id(user_id):
    user = get_db().execute(
        'SELECT id,username FROM user WHERE id=?',(user_id,)
    ).fetchone()
    return user

@bp.route('/user/<int:user_id>', methods=('GET', ))
def show_user_page(user_id:int):
    posts = get_post_for_user_id(user_id=user_id)
    user = get_user_from_id(user_id=user_id)

    return render_template('user/user_page.html',posts=posts, user=user)