import os
from flask import Flask
from flaskext.markdown import Markdown  #hay que cambiar la importacion de markdown en la librería!!!


# flask --app blog run --debug

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'blog.sqlite'),
    )
    md = Markdown(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from blog.views import db
    db.init_app(app)

    from blog.views import auth
    app.register_blueprint(auth.bp)

    from blog.views import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from blog.views import like
    app.register_blueprint(like.bp)

    from blog.views import comment
    app.register_blueprint(comment.bp)

    from blog.views import tag
    app.register_blueprint(tag.bp)

    from blog.views import user
    app.register_blueprint(user.bp)


    return app