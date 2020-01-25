# -*- coding: utf-8 -*-
import os
from flask import Flask


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    database_path = ''.join([app.root_path, '/../database/'])
    app.config.from_mapping(
        DEBUG=True,
        ENV='development',
        SECRET_KEY='dev',
        DATABASE=os.path.join(database_path, 'flask_demo.sqlite'),
    )
    # ensure the instance folder exists
    try:
        os.makedirs(database_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)
    db.get_db()

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
