import os
from flask import Flask

def create_app(config_filename):
    """ Handles configuration, registration, and other setup the Flask application needs.
    Also known as \"the application factory\". """
    
    app = Flask(__name__)
    app.config.from_pyfile('config.cfg', silent=True)
    
    try:
        app.config.from_envvar('OVIL_CUSTOM_CONFIG')
    except:
        pass
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from ovil.db_module import config_app
    config_app(app)

    from . import logger
    app.register_blueprint(logger.bp)
    app.add_url_rule('/', endpoint='home')

    return app