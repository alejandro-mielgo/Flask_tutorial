import os

from flask import Flask

# flask --app flaskr run --debug

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from flaskr.views import db
    db.init_app(app)

    from flaskr.views import auth
    app.register_blueprint(auth.bp)

    from flaskr.views import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from flaskr.views import like
    app.register_blueprint(like.bp)

    from flaskr.views import comment
    app.register_blueprint(comment.bp)

    from flaskr.views import tag
    app.register_blueprint(tag.bp)

    from flaskr.views import user
    app.register_blueprint(user.bp)


    return app