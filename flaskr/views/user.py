from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required, owner_of_page
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
        'SELECT id,username,name,surname,email,telephone FROM user WHERE id=?',(user_id,)
    ).fetchone()
    return user


@bp.route('/user/<int:user_id>', methods=('GET', ))
def show_user_page(user_id:int):
    posts = get_post_for_user_id(user_id=user_id)
    user = get_user_from_id(user_id=user_id)

    return render_template('user/user_page.html',posts=posts, user=user)


@bp.route('/user/<int:user_id>/edit', methods=('GET','POST'))
@owner_of_page
def edit_user_info(user_id:int):
    user = get_user_from_id(user_id=user_id)

    if request.method == 'GET':
        return render_template('user/user_page_edit.html', user=user)

    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    telephone = request.form['telephone']
    
    db=get_db()
    db.execute('UPDATE user'
                ' SET name=?,surname=?, email=?, telephone=?'
                ' WHERE id = ?',(name,surname,email,telephone,user['id']))
    db.commit()
    user = get_user_from_id(user_id=user_id)

    return render_template('user/user_page.html', user=user)


@bp.route('/api/user/<int:user_id>', methods=('GET', ))
def api_get_user_info(user_id:int):
    user = get_user_from_id(user_id=user_id)
    return dict(user)