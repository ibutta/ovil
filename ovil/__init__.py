import os
from flask import Flask
import ssl

def create_app(test_config=None):
    """ Handles configuration, registration, and other setup the Flask application needs.
    Also known as \"the application factory\". """
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = b',\xf4\xc5\xb0*\xb9\xfc\xb6'
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
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
    app.add_url_rule('/', endpoint='home')

    # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    # context.load_cert_chain('')

    # app.config.

    return app