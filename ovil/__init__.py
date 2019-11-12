import os
from flask import Flask
from flask_caching import Cache
from . import aux_funcs

cache = Cache()

def create_app():
    """ Handles configuration, registration, and other setup the Flask application needs.
    Also known as \"the application factory\". """
    
    app = Flask(__name__, 
        instance_path='{0}/.ovil-instance'.format(os.environ['HOME']), 
        instance_relative_config=True)

    app.config.from_pyfile('ovil-config.cfg', silent=True)
    # app.config.from_pyfile('ovil-config.ini', silent=True)
    
    try:
        os.makedirs(app.instance_path)
        aux_funcs.create_config_file(app.instance_path)

    except FileExistsError:
        if not os.path.exists('{0}/ovil-config.cfg'.format(app.instance_path)):
            aux_funcs.create_config_file(app.instance_path)
        print(' * Folder "ovil-instance" already exists. OK!')
        pass
    except OSError:
        print(' * *** ERROR creating "$HOME/.ovil-instance" folder! ***')
        pass
    else:
        print(' * Successfully created "ovil-instance" folder!')

    cache.init_app(app, config={'CACHE_TYPE': 'simple'})

    from ovil.db_module import config_app
    config_app(app)

    from . import logger
    app.register_blueprint(logger.bp)
    app.add_url_rule('/', endpoint='home')

    return app