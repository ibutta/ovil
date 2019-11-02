class Config(object):
    SECRET_KEY = b',\xf4\xc5\xb0*\xb9\xfc\xb6'
    # DB_NAME = "production-db"
    # DB_USERNAME = "admin"
    # DB_PASSWORD = "example"

    # IMAGE_UPLOADS = "/home/username/app/app/static/images/uploads"

    # SESSION_COOKIE_SECURE = True

class ProdConfig(Config):
    pass

class DevConfig(Config):

    # DB_NAME = "development-db"
    # DB_USERNAME = "admin"
    # DB_PASSWORD = "example"

    # IMAGE_UPLOADS = "/home/username/projects/my_app/app/static/images/uploads"

    # SESSION_COOKIE_SECURE = False