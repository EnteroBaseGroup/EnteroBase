import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') 
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') 
    FLASKY_MAIL_SUBJECT_PREFIX = '[Enterobase]'
    FLASKY_MAIL_SENDER = 'Enterobase Administrator'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    USER_DATABASE_URI  = os.environ.get('DEV_USERS_DATABASE_URL') 
    MAIL_SUPPRESS_SEND = False
    MAIL_FAIL_SILENTLY = False
    TESTING=False
 
    
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:test@localhost/test_users"
    #os.environ.get('DEV_DATABASE_URL') or \
        #'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:test@localhost/test_database"
    #os.environ.get('TEST_DATABASE_URL') or \
        #'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
