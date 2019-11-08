import os
from flask import Flask
from flask_caching import Cache

cache = Cache()

def create_app():
    """ Handles configuration, registration, and other setup the Flask application needs.
    Also known as \"the application factory\". """
    
    app = Flask(__name__, instance_path='/var/ovil-instance', instance_relative_config=True)
    app.config.from_pyfile('ovil-config.cfg', silent=True)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    cache.init_app(app, config={'CACHE_TYPE': 'simple'})

    from ovil.db_module import config_app
    config_app(app)

    from . import logger
    app.register_blueprint(logger.bp)
    app.add_url_rule('/', endpoint='home')

    return app