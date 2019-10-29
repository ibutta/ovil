import os
from flask import Flask

def create_app(test_config = None):
    """ Handles configuration, registration, and other setup the Flask application needs.
    Also known as \"the application factory\". """
    
    app = Flask(__name__, instance_relative_config = True)
    # app.config.from_mapping

    if test_config is None:
        app.config.from_pyfile('config.py', silent = True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.config_app(app)

    from . import logger
    app.register_blueprint(logger.bp)

    return app