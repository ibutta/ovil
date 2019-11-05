from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from flask import current_app, g
from ovil.aux_funcs import debug_print

def get_db(URI: str = ''):
    if 'db' not in g:
        if URI:
            g.db = MongoClient(URI)
        else:
            g.db = MongoClient()
        try:
            # a lightweight command to check if the connection
            # to the db was successfully established
            g.db.admin.command('ismaster')
        except:
            debug_print('Unable to connect to DB server...', func_name='get_db')
            return None
        else:
            return g.db
    return g.db

def close_db(err = None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def config_app(app):
    app.teardown_appcontext(close_db)