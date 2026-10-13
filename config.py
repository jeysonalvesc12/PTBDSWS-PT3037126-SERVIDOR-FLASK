import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'Chave forte'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = os.environ.get('API_KEY')
    API_URL = os.environ.get('API_URL')
    API_FROM = os.environ.get('API_FROM')
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    PROF_EMAIL = os.environ.get('PROF_EMAIL')

    @staticmethod
    def init_app(app):
        pass        